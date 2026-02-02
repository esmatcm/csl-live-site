# CSL Live Site

## Deployment Order (Must Follow)
1. Update/Upload `data.json` to Baota (`/www/wwwroot/hsapi.xyz/data.json`).
2. Only after remote job_id matches, update Mission Control `DEPLOYS/hsapi/latest.json`.

Reason: avoid job mismatch during verification.
