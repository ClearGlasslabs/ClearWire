from datetime import datetime, timezone
from fastapi import HTTPException

MIN_K = 5


def aggregate_exposure(scope_id: str, k: int = MIN_K) -> dict:
    if k < MIN_K:
        raise HTTPException(status_code=400, detail=f'Credential exposure queries require k >= {MIN_K}')
    # Deliberately aggregate-only: no usernames, passwords, hashes, tokens, or source payloads.
    return {
        'scope_id': scope_id,
        'privacy_model': 'k-anonymity',
        'k': k,
        'plaintext_credentials_stored': False,
        'credential_material_collected': False,
        'result': 'No exposed credential material returned by simulator',
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }
