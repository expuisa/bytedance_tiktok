** NEEDS TIKTOK SDK FOR BOGUS **

from py_mini_racer import py_mini_racer

# Load webmssdk.js contents
with open("sdk/webmssdk.js", "r", encoding="utf-8") as f:
    webmssdk_js = f.read()

# Create JavaScript code block
js_code = f"""
{webmssdk_js}
function generateXbogus(query) {{
    return _0x32d649(query);
}}
"""

# Create JS runtime
ctx = py_mini_racer.MiniRacer()
ctx.eval(js_code)

# Example query string (after ? in URL)
query = "aid=1988&app_name=tiktok_web&device_platform=web"

# Generate X-Bogus
xbogus = ctx.call("generateXbogus", query)
print(f"X-Bogus: {xbogus}")
