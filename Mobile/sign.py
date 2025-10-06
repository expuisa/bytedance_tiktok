from signer import md5, gorgon, ladon, argus
from time   import time

def sign(params: str, payload: str or None = None, sec_device_id: str = '', cookie: str or None = None, aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = 'v05.00.03-ov-android', sdk_version: int = 167773760, platform: int = 0, unix: float = None):
    x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload != None else None
    if not unix: unix = time()

    return gorgon.Gorgon(params, unix, payload, cookie).get_value() | {
        'x-ss-stub'      : x_ss_stub.upper(),
        'X-Ladon'        : ladon.Ladon.encrypt(int(unix), license_id, aid),
        'X-Argus'        : argus.Argus.get_sign(params, x_ss_stub, int(unix),
            platform        = platform,
            aid             = aid,
            license_id      = license_id,
            sec_device_id   = sec_device_id,
            sdk_version     = sdk_version_str, 
            sdk_version_int = sdk_version
        )
    }
