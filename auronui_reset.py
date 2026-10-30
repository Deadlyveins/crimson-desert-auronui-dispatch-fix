#!/usr/bin/env python3
"""
Crimson Desert: Auronui Island pioneering dispatch. Experimental two-stage workaround.

v0.4.6 beta: supports both observed operation layouts and independent metadata fields.
The progress number is NOT a proven indicator of a broken dispatch; there is no
numeric eligibility threshold. Repairs require an explicit user decision.
The two-stage workflow is experimentally verified on multiple players' saves;
full quest completion is not confirmed for every sample.

This is not a generic quest fixer. The original input is NEVER overwritten.
The checks intentionally refuse unfamiliar saves, even if the symptom looks similar.
Requires Python 3.11+, cryptography, and lz4.
"""

import argparse
import hashlib
import hmac
import os
import struct
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import math

import lz4.block
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

HEADER_SIZE = 0x80
OPERATION_ID = 0xE4BE83E8
FACTION_NODE_ID = 1001022
TOOL_VERSION = "0.4.6-beta"

# A strict fingerprint from observed 64-byte records, with three variable
# 32-bit fields and a progress float treated as dynamic. These three fields
# do NOT have to match each other, as demonstrated by the third player's save.
# The 56-byte layout uses independent field-level validations below.
# Neither validation profile is guaranteed to cover all valid save states.
RECORD_SIZE = 64
KNOWN_RECORD_TEMPLATE = bytes.fromhex(
    "e8 83 be e4 14 cc 29 1b 02 00 00 00 14 cc 29 1b 02 00 00 00 "
    "dc 03 0c 24 02 00 00 00 0a 01 ed 43 80 84 1e 00 "
    "00 00 00 00 00 00 80 7f 00 03 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 01 00"
)
assert len(KNOWN_RECORD_TEMPLATE) == RECORD_SIZE
DYNAMIC_BYTES = (set(range(4, 8)) | set(range(12, 16))
                 | set(range(20, 24)) | set(range(28, 32)))

# The progress field is a finite float in each observed save, but its
# *meaning* and any normal bounds are unverified. Do NOT classify a dispatch
# as broken or healthy using the counter alone. Some previously stuck saves
# were below the old artificial 400 cutoff.
# Stage 2 intentionally requires the user to confirm they loaded the Stage 1
# output and made a NEW in-game save. Its preflight can't prove that sequence.
BASE = bytes.fromhex('C41B8E730DF259A637CC04E9B12F9668DA107A853E61F9224DB80AD75C13EF90')[:31]
PREFIX = {1: b'^Qgbrm/.#@`zsr]\\@rvfal#"', 2: b'^Pearl--#Abyss__@!!'}


def save_key(version: int) -> bytes:
    if version not in PREFIX:
        raise ValueError(f'Unsupported SAVE version {version} (only 1 and 2 are supported).')
    material = PREFIX[version] + b'PRIVATE_HMAC_SECRET_CHECK'
    return bytes(a ^ b for a, b in zip(BASE, material)) + b'\x00'


def decode_save(data: bytes) -> tuple[bytes, int]:
    if len(data) < HEADER_SIZE or data[:4] != b'SAVE':
        raise ValueError('This is not a recognized Crimson Desert SAVE file.')
    version = struct.unpack_from('<H', data, 4)[0]
    key = save_key(version)
    raw_size, encrypted_size = struct.unpack_from('<II', data, 0x12)
    if raw_size <= 0 or encrypted_size <= 0 or encrypted_size != len(data) - HEADER_SIZE:
        raise ValueError('SAVE header lengths are unexpected; no changes made.')
    nonce = data[0x1A:0x2A]
    compressed = Cipher(algorithms.ChaCha20(key, nonce), mode=None).decryptor().update(data[HEADER_SIZE:])
    expected = hmac.new(key, compressed, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, data[0x2A:0x4A]):
        raise ValueError('SAVE HMAC does not match; refusing to patch.')
    decompressed = lz4.block.decompress(compressed, uncompressed_size=raw_size)
    if len(decompressed) != raw_size:
        raise ValueError('Unexpected decompressed length; no changes made.')
    return decompressed, version


@dataclass(frozen=True)
class OperationMatch:
    field_pos: int
    field_value: float
    op_pos: int
    assigned_workers: int
    layout: str
    record_size: int


def _all_offsets(payload: bytes, needle: bytes) -> list[int]:
    positions = []
    start = 0
    while True:
        pos = payload.find(needle, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def locate_auronui_record(payload: bytes) -> OperationMatch:
    """Read-only structural preflight for two *observed* dispatch layouts.

    Both layouts have been identified and tested in-game, but this does not
    establish that every future game version or dispatch state is supported.
    A rejected save is deliberately never patched.
    """
    candidates = _all_offsets(payload, struct.pack('<I', OPERATION_ID))
    if len(candidates) != 1:
        raise ValueError(
            f'Preflight failed: expected exactly one Auronui operation ID, '
            f'found {len(candidates)}. The quest may be at another state, ' 
            'or this may be the wrong save slot. No changes made.'
        )
    op = candidates[0]
    if op < 80 or op + RECORD_SIZE + 16 > len(payload):
        raise ValueError('Preflight failed: Auronui operation is truncated.')
    node = struct.pack('<I', FACTION_NODE_ID)
    if payload[op-45:op].count(node) < 2:
        raise ValueError('Preflight failed: matching Auronui node context is missing.')

    # Three neighboring 8-byte records all have the same operation kind.
    # Their 32-bit values may be equal OR DIFFERENT; the third player's file
    # demonstrates distinct, nonzero values. The previous tag_a == tag_b
    # requirement incorrectly rejected this valid observed structure.
    # Their exact semantics (timestamps, handles, etc.) are not established.
    fields = [struct.unpack_from('<II', payload, op + offset)
              for offset in (4, 12, 20)]
    tags = [item[0] for item in fields]
    kinds = [item[1] for item in fields]
    if not all(tags) or len(set(kinds)) != 1:
        raise ValueError('Preflight failed: operation metadata fields are inconsistent.')
    kind_a = kinds[0]
    if kind_a not in (1, 2):
        raise ValueError(f'Preflight failed: unsupported dispatch kind {kind_a}.')
    # Known neighboring serialized context, present in independent saves.
    if payload[op-51:op-49] != bytes.fromhex('5b42'):
        raise ValueError('Preflight failed: expected neighboring record marker is missing.')
    if payload[op-27:op-17] != bytes.fromhex('003e460f00003e460f00'):
        raise ValueError('Preflight failed: neighboring faction metadata differs.')

    # 64-byte layout: optional 8-byte timer/resource slot exists after progress.
    # 56-byte layout: optional slot is absent, moving the sentinel 8 bytes.
    # No broad byte scans: fixed offsets only for the two observed profiles.
    if kind_a == 2:
        layout = '64-byte layout'
        record_size = 64
        sentinel = op + 40
        core = payload[op:op + record_size]
        bad = [i for i in range(record_size)
               if i not in DYNAMIC_BYTES and core[i] != KNOWN_RECORD_TEMPLATE[i]]
        if bad:
            raise ValueError(f'Preflight failed: unfamiliar 64-byte record '
                             f'(first offset(s): {bad[:8]}). No changes made.')
        if payload[op+32:op+40] != bytes.fromhex('80841e0000000000'):
            raise ValueError('Preflight failed: 64-byte optional data differs.')
    else:
        layout = '56-byte layout'
        record_size = 56
        sentinel = op + 32
        # Require the exact observed sentinel/flag encoding, but permit the
        # player-specific tag to vary when all its redundant copies agree.
        if payload[op+38:op+54] != b'\x00' * 16:
            raise ValueError('Preflight failed: unfamiliar 56-byte flags. No changes made.')
        if payload[op+54:op+56] != b'\x01\x00':
            raise ValueError('Preflight failed: unfamiliar 56-byte ending. No changes made.')

    if payload[sentinel:sentinel+4] != b'\x00\x00\x80\x7f':
        raise ValueError('Preflight failed: operation sentinel is missing.')
    if payload[sentinel+4] != 0:
        raise ValueError('Preflight failed: unexpected operation-state encoding.')
    workers = payload[sentinel+5]
    if workers != 3:
        raise ValueError(f'Preflight failed: expected 3 Greymanes, found {workers}.')
    # In both samples, a marker for the first assigned worker immediately
    # follows the core record; its identifier can legitimately vary.
    follower = payload[op+record_size:op+record_size+16]
    if (follower[0] != 1 or follower[2:4] != b'\x00\x00'
            or follower[4:12] != b'\xff'*8):
        raise ValueError('Preflight failed: assigned-worker list layout differs.')
    # All post-sentinel bytes, besides worker count, must be known zeroes.
    if payload[sentinel+6:op+record_size-2] != b'\x00' * (record_size - 2 - (sentinel + 6 - op)):
        raise ValueError('Preflight failed: unexpected dispatch flags after worker count.')
    if payload[op+record_size-2:op+record_size] != b'\x01\x00':
        raise ValueError('Preflight failed: dispatch core ending differs.')

    value = struct.unpack_from('<f', payload, op+28)[0]
    if not math.isfinite(value):
        raise ValueError('Preflight failed: dispatch progress is not finite.')
    return OperationMatch(op+28, value, op, workers, layout, record_size)


def locate_auronui_field(payload: bytes) -> OperationMatch:
    """Stage 1: identify the operation, not whether it is really broken.

    The counter is intentionally NOT subject to arbitrary minimum/maximum
    thresholds. A snapshot cannot determine whether a dispatch is stuck.
    """
    return locate_auronui_record(payload)


def encode_save(source: bytes, payload: bytes, version: int) -> bytes:
    header = bytearray(source[:HEADER_SIZE])
    compressed = lz4.block.compress(payload, mode='high_compression', compression=9, store_size=False)
    nonce = os.urandom(16)
    key = save_key(version)
    encrypted = Cipher(algorithms.ChaCha20(key, nonce), mode=None).encryptor().update(compressed)
    struct.pack_into('<II', header, 0x12, len(payload), len(encrypted))
    header[0x1A:0x2A] = nonce
    header[0x2A:0x4A] = hmac.new(key, compressed, hashlib.sha256).digest()
    return bytes(header) + encrypted


def locate_stage2_field(payload: bytes) -> OperationMatch:
    """Stage 2 preflight for either in-game tested layout."""
    match = locate_auronui_record(payload)
    # Counter range cannot prove whether Stage 1 was performed, nor whether
    # the dispatch is stuck. In-game resave is required by workflow, not
    # inferred from a guessed counter threshold.
    op = match.op_pos
    if payload[op-51:op-49] != bytes.fromhex('5b42'):
        raise ValueError('Stage 2 metadata marker at -51 differs; refusing.')
    expected_metadata = 0x92 if match.record_size == 64 else 0x90
    if payload[op-47] != expected_metadata or payload[op-46] != 0:
        raise ValueError('Stage 2 adjacent metadata differs; refusing.')
    if payload[op-27:op-17] != bytes.fromhex('003e460f00003e460f00'):
        raise ValueError('Stage 2 adjacent Auronui node list differs; refusing.')
    if payload[op-23] != 0:
        raise ValueError('Stage 2 serialized node-list byte not zero; refusing.')
    if match.record_size == 64:
        if payload[op+32:op+40] != bytes.fromhex('80841e0000000000'):
            raise ValueError('Stage 2 64-byte resource slot differs; refusing.')
    elif match.record_size == 56:
        if payload[op+32:op+36] != bytes.fromhex('0000807f'):
            raise ValueError('Stage 2 56-byte sentinel differs; refusing.')
    else:
        raise ValueError('Stage 2 unrecognized record layout; refusing.')
    return match


def apply_stage2(payload: bytes, match: OperationMatch) -> bytes:
    """Localized, reversible state-activation edit for either validated profile.

    Both edit variants have started dispatch in-game on the observed saves.
    They are not proven safe for arbitrary other saves, so preflight remains strict.
    """
    op = match.op_pos
    if (payload[op-51] != 0x5B or payload[op-47] not in (0x90, 0x92)
            or payload[op-23] != 0):
        raise ValueError('Stage 2 local validation failed. No changes made.')
    modified = bytearray(payload)
    modified[op-51] = 0x59
    modified[op-47] += 1
    del modified[op-23]
    new_op = op - 1
    modified[new_op+32:new_op+32] = b'\x01'
    if len(modified) != len(payload):
        raise RuntimeError('Stage 2 payload length mismatch; refusing.')
    # All content after insertion remains byte-identical. The only edits
    # permitted are the two metadata byte changes, node-list byte removal,
    # and insertion of an explicit operation-state byte.
    if modified[:op-51] != payload[:op-51]:
        raise RuntimeError('Unexpected changes before operation.')
    if modified[op+32:] != payload[op+32:]:
        raise RuntimeError('Unexpected changes after operation-state insertion.')
    if modified[new_op:new_op+32] != payload[op:op+32]:
        raise RuntimeError('Operation core was unexpectedly modified.')
    if modified[new_op+32] != 1:
        raise RuntimeError('Operation state flag was not inserted.')
    operation_id = struct.pack('<I', OPERATION_ID)
    if _all_offsets(modified, operation_id) != [new_op]:
        raise RuntimeError('Operation ID shifted unexpectedly.')
    # Undo exact modifications to verify reversibility byte-for-byte.
    reverse = bytearray(modified)
    del reverse[new_op+32]
    reverse[op-23:op-23] = b'\x00'
    reverse[op-51] = 0x5B
    reverse[op-47] -= 1
    if bytes(reverse) != payload:
        raise RuntimeError('Stage 2 did not fully roundtrip to original bytes.')
    return bytes(modified)


def main() -> int:
    parser = argparse.ArgumentParser(description='Crimson Desert Auronui two-stage experimental save repair v0.4.6-beta. NEVER edits your input.')
    parser.add_argument('save', type=Path, help='Path to save.save, preferably a COPY')
    parser.add_argument('--stage', choices=['1','2'], default='1',
                        help='Stage 1: reset operation counter; Stage 2: reactivate dispatch AFTER loading Stage 1 and saving in-game.')
    parser.add_argument('--check', action='store_true', help='Preflight only; write nothing.')
    parser.add_argument('--yes', action='store_true', help='Accept the prompt only for automated regression testing.')
    parser.add_argument('--after-ingame-resave', action='store_true',
                        help='Required to WRITE Stage 2. Confirms you loaded Stage 1 into the game, saved again in-game, then exited.')
    args = parser.parse_args()
    source_file = args.save.expanduser().resolve()
    if not source_file.is_file():
        raise ValueError(f'Cannot find save file: {source_file}')
    source = source_file.read_bytes()
    raw, version = decode_save(source)
    if version != 2:
        raise ValueError(f'SAVE version {version} unsupported; refusing.')
    if args.stage == '1':
        match = locate_auronui_field(raw)
        print(f'STAGE 1: Found Auronui operation with counter {match.field_value:.6f}.')
        print('This stage resets the dispatch COUNTER only; it does NOT diagnose a bug.')
        print('WARNING: We cannot tell whether your operation is healthy or stuck.')
        print('Use ONLY if the in-game dispatch is genuinely stuck. No arbitrary counter limits.')
        if struct.unpack_from('<I', raw, match.field_pos)[0] == 0:
            print('NOTE: Counter is already positive zero; Stage 1 would make no change.')
    else:
        match = locate_stage2_field(raw)
        print(f'STAGE 2: Found recognizable operation record, counter {match.field_value:.6f}.')
        print('This stage inserts the operation-state flag and adjusts adjacent metadata.')
        print('WARNING: A matching record CANNOT prove that Stage 1 has been performed!')
        print('Use ONLY on a NEW IN-GAME SAVE made after loading Stage 1, and')
        print('ONLY if pressing Dispatch still does absolutely nothing.')
    print(f'LAYOUT: {match.layout}')
    print('IMPORTANT: Greymane faction quests may fail as Damiane or Oongka.')
    print('TRY SWITCHING TO KLIFF IN GAME BEFORE ANY SAVE EDIT.')
    print('Both 56-byte and 64-byte layouts have been observed in separate saves.')
    print('A structural match does NOT guarantee that this game version is compatible.')
    print(f'SAVE v{version} | {len(raw):,} unpacked bytes | faction node {FACTION_NODE_ID} | 3 workers')
    print('Preflight PASSED for the requested stage.')
    if args.check:
        print('CHECK ONLY: no output created, no changes made.')
        return 0
    if args.stage == '1' and struct.unpack_from('<I', raw, match.field_pos)[0] == 0:
        print('Stage 1 not applied: this progress field is already 0.0.')
        print('Load this save in game and resave if needed; do not mistake a no-op for a repair.')
        return 2
    if args.stage == '2' and not args.after_ingame_resave:
        raise ValueError('Stage 2 requires --after-ingame-resave. First load the Stage 1 '
                         'save in-game, save again in-game, exit, then use that new save.')
    confirmation = 'RESET' if args.stage == '1' else 'REACTIVATE'
    if not args.yes and input(f'Type {confirmation} to create a NEW experimental save: ').strip() != confirmation:
        print('Cancelled without modifying anything.')
        return 2
    if args.stage == '1':
        edited = bytearray(raw)
        struct.pack_into('<f', edited, match.field_pos, 0.0)
        patched = bytes(edited)
        diff = [i for i, (a,b) in enumerate(zip(raw,patched)) if a!=b]
        if not diff or any(i not in range(match.field_pos,match.field_pos+4) for i in diff):
            raise RuntimeError('Stage 1 modified unexpected bytes; refusing output.')
    else:
        patched = apply_stage2(raw, match)
    encoded = encode_save(source, patched, version)
    check, check_version = decode_save(encoded)
    if check_version != version or check != patched:
        raise RuntimeError('Output decryption/integrity roundtrip failed.')
    if source_file.read_bytes() != source:
        raise RuntimeError('Input changed during patch; no files written.')
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    backup = source_file.with_name(source_file.name+f'.ORIGINAL_{stamp}.bak')
    output = source_file.with_name(source_file.stem+f'_AURONUI_STAGE{args.stage}_{stamp}.save')
    with backup.open('xb') as fp: fp.write(source)
    if backup.read_bytes() != source:
        backup.unlink(missing_ok=True)
        raise RuntimeError('Backup verification failed; no patch written.')
    with output.open('xb') as fp: fp.write(encoded)
    if decode_save(output.read_bytes())[0] != patched:
        output.unlink(missing_ok=True)
        raise RuntimeError('Saved output integrity failed, preserving backup.')
    print('\nSUCCESS. ORIGINAL UNTOUCHED.')
    print('Backup :',backup)
    print('TEST   :',output)
    print('SHA-256 original:',hashlib.sha256(source).hexdigest())
    print('SHA-256 patched :',hashlib.sha256(encoded).hexdigest())
    print('Rename a COPY of TEST to save.save in your TEST slot. Never overwrite only backup.')
    if args.stage == '1':
        print('Next: load test save as KLIFF at Auronui. If the dispatch starts, STOP.')
        print('Only if Dispatch still does nothing: save again IN-GAME, close')
        print('the game, and run Stage 2 on a COPY of that newly saved file.')
    else:
        print('Next: load test save AS KLIFF at Auronui. Verify dispatch STARTS, progresses, and actually completes.')
        print('Stop if anything behaves unexpectedly. Restore your unmodified backup.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Exception, KeyboardInterrupt) as exc:
        print('\nERROR:', exc, file=sys.stderr)
        sys.exit(1)
