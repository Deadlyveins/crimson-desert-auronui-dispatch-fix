#!/usr/bin/env python3
"""
Crimson Desert Auronui pioneering dispatch: experimental two-stage repair.

Strict preflight checks the known operation signature, node, worker count,
masked 64-byte record fingerprint, and numeric counter range observed in two stuck saves.
These checks CANNOT prove the in-game quest is broken; unknown saves are rejected.

Original input is never overwritten. Requires Python 3.11+, cryptography, lz4.
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
TOOL_VERSION = "0.4.1 PUBLIC BETA / EXPERIMENTAL"

# A masked structural fingerprint from TWO original, stuck Auronui saves.
# It covers the ENTIRE 64-byte core dispatch record, not just the operation ID.
# Only the known dynamic 4-byte time marker at [20:24] and 4-byte progress
# value at [28:32] are allowed to vary. Everything else must match exactly.
# Overly strict rejection is intentional: never modify unfamiliar layouts.
# This is a template of operation structure, NOT a universal save schema.
RECORD_SIZE = 64
KNOWN_RECORD_TEMPLATE = bytes.fromhex(
    "e8 83 be e4 14 cc 29 1b 02 00 00 00 14 cc 29 1b 02 00 00 00 "
    "dc 03 0c 24 02 00 00 00 0a 01 ed 43 80 84 1e 00 "
    "00 00 00 00 00 00 80 7f 00 03 00 00 00 00 00 00 "
    "00 00 00 00 00 00 00 00 00 00 01 00"
)
assert len(KNOWN_RECORD_TEMPLATE) == RECORD_SIZE
DYNAMIC_BYTES = set(range(20, 24)) | set(range(28, 32))

# Observed in two stuck 100% saves: 474.008 and 506.555.
# Values outside this conservative range are refused to protect active dispatches.
# Not a proven game-engine completion threshold.
SUSPECTED_COMPLETE_MIN = 400.0
SUSPECTED_COMPLETE_MAX = 2000.0
# Stage 2 ONLY: our manually verified successful state1 patch was applied to
# an in-game re-saved, partially reset dispatch with counter 14.55.
STAGE_2_MIN = 0.001
STAGE_2_MAX = 100.0
# These adjacent identifiers were consistent in the original stuck save,
# and the subsequent in-progress save from the same playthrough.
OPERATION_PREFIX = (struct.pack('<I', OPERATION_ID)
                    + bytes.fromhex('14cc291b0200000014cc291b02000000'))
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


def locate_auronui_field(payload: bytes) -> OperationMatch:
    """Reject saves not matching the *known* potentially stuck operation.

    This is deliberately conservative and is NOT a general Crimson Desert
    quest-fixer. Only evidence for one exact dispatch layout is available.
    """
    starts = []
    start = 0
    while True:
        found = payload.find(OPERATION_PREFIX, start)
        if found == -1:
            break
        starts.append(found)
        start = found + 1
    if len(starts) != 1:
        raise ValueError(
            f'Preflight failed: expected exactly one known Auronui operation '
            f'(found {len(starts)}). This save will NOT be patched.'
        )
    op_pos = starts[0]
    if op_pos < 45 or op_pos + RECORD_SIZE > len(payload):
        raise ValueError('Preflight failed: Auronui operation record is truncated.')

    node_bytes = struct.pack('<I', FACTION_NODE_ID)
    # This adjacency was observed in the affected game saves.
    # Count is a structural heuristic, not an independently documented format.
    context = payload[op_pos - 45:op_pos]
    if context.count(node_bytes) < 2:
        raise ValueError('Preflight failed: matching Auronui node context is missing.')

    # Whole-core masked comparison: time/progress may legitimately differ,
    # but all 56 other bytes must match BOTH previously observed stuck saves.
    core = payload[op_pos:op_pos + RECORD_SIZE]
    unexpected = [i for i in range(RECORD_SIZE)
                  if i not in DYNAMIC_BYTES and core[i] != KNOWN_RECORD_TEMPLATE[i]]
    if unexpected:
        detail = ', '.join(str(i) for i in unexpected[:8])
        raise ValueError(
            f'Preflight failed: unknown dispatch record layout (offset(s) {detail}). '
            'This save is NOT patched. Do not bypass this safeguard.'
        )
    # Extra layout checks help reject similar/random operation records.
    # All constants are from actual affected samples (not generic game flags).
    if struct.unpack_from('<I', payload, op_pos + 32)[0] != 2_000_000:
        raise ValueError('Preflight failed: dispatch timer/layout differs from known affected saves.')
    if payload[op_pos + 40:op_pos + 44] != b'\x00\x00\x80\x7f':
        raise ValueError('Preflight failed: operation sentinel/layout differs from known affected saves.')
    if payload[op_pos + 44] != 0:
        raise ValueError('Preflight failed: operation-state layout differs from known affected saves.')

    worker_count = payload[op_pos + 45]
    if worker_count != 3:
        raise ValueError(
            f'Preflight failed: expected 3 assigned Greymanes, '
            f'found {worker_count}. No changes made.'
        )

    field_pos = op_pos + 28
    value = struct.unpack_from('<f', payload, field_pos)[0]
    if not math.isfinite(value):
        raise ValueError('Preflight failed: operation counter is not finite.')
    if not SUSPECTED_COMPLETE_MIN <= value <= SUSPECTED_COMPLETE_MAX:
        raise ValueError(
            f'Preflight failed: Auronui operation found, but counter {value:.3f} '
            f'is outside the conservative suspected-stuck range '
            f'[{SUSPECTED_COMPLETE_MIN:g}, {SUSPECTED_COMPLETE_MAX:g}]. '
            'This may be a healthy/in-progress or differently bugged dispatch. '
            'No changes made.'
        )
    return OperationMatch(field_pos, value, op_pos, worker_count)


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
    """Strictly match the partial-reset record for the manual state1 patch.

    IMPORTANT: A small counter does not prove the dispatch is broken.
    Users must independently verify Dispatch does NOTHING before using stage 2.
    """
    match = locate_auronui_record(payload)
    if not STAGE_2_MIN <= match.field_value <= STAGE_2_MAX:
        raise ValueError(f'Stage 2 expects the game-resaved partially reset dispatch; '
                         f'counter {match.field_value:.3f} outside '
                         f'[{STAGE_2_MIN}, {STAGE_2_MAX}]. No changes made.')
    op = match.op_pos
    if payload[op-51:op-49] != bytes.fromhex('5b42'):
        raise ValueError('Stage 2 context marker A differs; refusing modification.')
    if payload[op-47:op-45] != bytes.fromhex('9200'):
        raise ValueError('Stage 2 context marker B differs; refusing modification.')
    if payload[op-27:op-17] != bytes.fromhex('003e460f00003e460f00'):
        raise ValueError('Stage 2 adjacent record structure differs; refusing modification.')
    if payload[op+32:op+36] != bytes.fromhex('80841e00'):
        raise ValueError('Stage 2 operation-state slot is not absent as expected.')
    return match


def locate_auronui_record(payload: bytes) -> OperationMatch:
    """All structural checks, but no counter range, reusable for both stages."""
    # Our original locator contains the same checks plus a final counter range.
    # Handle its conservative final-range failure ONLY if the remaining structure
    # passes each explicit check here; never ignore other failures.
    starts = []
    pos = 0
    while True:
        op = payload.find(OPERATION_PREFIX, pos)
        if op < 0: break
        starts.append(op)
        pos = op + 1
    if len(starts) != 1:
        raise ValueError(f'Expected exactly 1 known operation, found {len(starts)}.')
    op = starts[0]
    if op < 60 or op + RECORD_SIZE > len(payload):
        raise ValueError('Operation truncated.')
    node = struct.pack('<I', FACTION_NODE_ID)
    if payload[op-45:op].count(node) < 2:
        raise ValueError('Node context does not match known Auronui record.')
    core = payload[op:op + RECORD_SIZE]
    bad = [i for i in range(RECORD_SIZE)
           if i not in DYNAMIC_BYTES and core[i] != KNOWN_RECORD_TEMPLATE[i]]
    if bad:
        raise ValueError(f'Unknown operation layout at offsets {bad[:8]}.')
    if struct.unpack_from('<I', payload, op+32)[0] != 2_000_000:
        raise ValueError('Unexpected operation data after counter.')
    if payload[op+40:op+44] != b'\x00\x00\x80\x7f' or payload[op+44] != 0:
        raise ValueError('Unexpected operation-state encoding.')
    workers = payload[op+45]
    if workers != 3:
        raise ValueError(f'Expected three assigned workers, got {workers}.')
    value = struct.unpack_from('<f', payload, op+28)[0]
    if not math.isfinite(value):
        raise ValueError('Invalid progress float.')
    return OperationMatch(op+28,value,op,workers)


def apply_stage2(payload: bytes, match: OperationMatch) -> bytes:
    """Replicate ACTUAL successful Test A, rather than the failed 4-byte-only tool.

    The successful Test A inserted an operation state 01, and adjusted the
    immediately adjacent byte-layout markers. It was not simply a counter reset.
    """
    op = match.op_pos
    modified = bytearray(payload)
    modified[op-51] = 0x59
    modified[op-47] = 0x93
    # Remove one redundant/optional zero byte in preceding serialized record.
    del modified[op-23]
    # One-byte operation state from the working Test A was 01, immediately
    # between the progress float and the fixed 0x001E8480 value.
    modified[op-1+32:op-1+32] = b'\x01'
    if len(modified) != len(payload):
        raise RuntimeError('Stage 2 modified overall payload size; refusing.')
    # Roundtrip relative checks; original record moves back by one byte due to deletion.
    new_op = modified.find(OPERATION_PREFIX)
    if new_op != op-1 or modified.count(OPERATION_PREFIX) != 1:
        raise RuntimeError('Stage 2 operation relocation failed validation.')
    if modified[new_op+32] != 1 or modified[new_op+33:new_op+37] != bytes.fromhex('80841e00'):
        raise RuntimeError('Stage 2 operation state insertion failed validation.')
    # Compare untouched areas exactly. All differences must be localized to
    # preceding markers and the operation itself, no unrelated item edits.
    if modified[:op-51] != payload[:op-51] or modified[op+33:] != payload[op+33:]:
        raise RuntimeError('Stage 2 modified bytes outside expected localized region.')
    return bytes(modified)


def main() -> int:
    parser = argparse.ArgumentParser(description='Crimson Desert Auronui two-stage experimental save repair. NEVER edits your input.')
    parser.add_argument('save', type=Path, help='Path to save.save, preferably a COPY')
    parser.add_argument('--stage', choices=['1','2'], default='1',
                        help='Stage 1: reset finished counter; Stage 2: reactivate partially-reset dispatch after in-game resave.')
    parser.add_argument('--check', action='store_true', help='Preflight only; write nothing.')
    parser.add_argument('--yes', action='store_true', help='Accept the prompt only for automated regression testing.')
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
        print(f'STAGE 1: Found stuck Auronui pattern with counter {match.field_value:.6f}.')
        print('This stage resets the dispatch COUNTER only; usually NOT sufficient to fix the quest.')
    else:
        match = locate_stage2_field(raw)
        print(f'STAGE 2: Found partial-reset record, counter {match.field_value:.6f}.')
        print('This stage reproduces the Test A operation state 01 and adjacent metadata edits.')
        print('WARNING: Cannot distinguish a healthy active dispatch from a broken one!')
        print('USE ONLY if game says Dispatch but confirming does NOTHING.')
    print(f'SAVE v{version} | {len(raw):,} unpacked bytes | faction node {FACTION_NODE_ID} | 3 workers')
    print('Preflight PASSED for the requested stage.')
    if args.check:
        print('CHECK ONLY: no output created, no changes made.')
        return 0
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
        print('Next: load test save in-game at Auronui, make a new manual save, CLOSE the game, then run STAGE 2 on that new save if Dispatch still does nothing.')
    else:
        print('Next: load test save at Auronui. Verify dispatch STARTS, progresses, and actually completes. Not publicly validated.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Exception, KeyboardInterrupt) as exc:
        print('\nERROR:', exc, file=sys.stderr)
        sys.exit(1)
