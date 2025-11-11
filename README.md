# TikTok Reverse Engineering - Mobile and Web API
#### Need Premium Solutions? @sequestrer On Telegram

A technical overview of TikTok's internal API security, focusing on the various signature algorithms used to authenticate and protect client-server communication. This document is intended for educational and research purposes.

**Disclaimer:** Interacting with private APIs without authorization may violate the terms of service of the platform. Proceed with caution and at your own risk.

---

### 1. Introduction to TikTok's API Security

To combat automated bots and ensure platform integrity, TikTok and its Chinese counterpart, Douyin, employ a sophisticated suite of security algorithms. These algorithms generate dynamic signatures that are attached as headers to most API requests. A request lacking a valid signature will be rejected by TikTok's servers.

These signatures are generated client-side (on the mobile app or web browser) and are designed to be difficult to replicate, proving that the request originates from a legitimate client instance. The primary algorithms are known by their HTTP header names:

-   `X-Argus`
-   `X-Gorgon`
-   `X-Bogus`
-   `X-Ladon`
-   `X-Typhon`
-   `X-Medusa` (More prevalent in Douyin)

While the global version of TikTok and Douyin share similar algorithmic foundations, their API endpoints and risk control strictness differ. Global TikTok's risk management is generally considered more aggressive.

---

### 2. Deep Dive into Signature Generation Algorithms

Based on reverse-engineering of the client-side code, we can detail the precise steps involved in generating the `X-Bogus` and `X-Argus` signatures.

#### **2.1. The X-Bogus Signature Algorithm**

The `X-Bogus` algorithm is a multi-stage process designed to create a unique signature from request data, user agent, and a timestamp. It relies heavily on hashing, custom ciphers, and data manipulation to achieve obfuscation.

**Core Constants and Configuration**
```python
SHIFT_ARRAY = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe"
MAGIC_NUMBER = 536919696
RC4_UA_KEY = [0, 1, 14]  # Key for user-agent encryption
RC4_FINAL_KEY = [255]    # Key for final encryption
```

**Required Parameters**
```python
{
    'params': str,      # URL query parameters
    'user_agent': str,  # Browser/Device User-Agent
    'timestamp': int,   # Current Unix timestamp
    'data': str        # Request body (optional)
}
```

**Step 1: Initial Hashing of Core Components**

The algorithm first computes three separate MD5 hashes to create a condensed and irreversible representation of the request's key elements.

1.  **Data Hashing**: Double MD5 hashing of the request body:
    ```python
    def md5_2x(string):
        return md5(md5(string.encode()).digest()).hexdigest()
    
    md5_data = md5_2x(data)
    ```

2.  **URL Parameters Hashing**: Same double MD5 process for URL parameters:
    ```python
    md5_params = md5_2x(params)
    ```

3.  **User-Agent Processing**: Three-step transformation:
    ```python
    # a. RC4 Encryption with key [0, 1, 14]
    encrypted_ua = rc4_encrypt(user_agent, [0, 1, 14])
    
    # b. Custom Base64 encoding
    b64_ua = b64_encode(encrypted_ua)
    
    # c. Final MD5 hash
    md5_ua = md5(b64_ua.encode()).hexdigest()
    ```

**Step 2: Assembling the "Salt Array"**

A core data array is created with precisely ordered components:
```python
salt_list = [
    timestamp,              # Current Unix timestamp
    536919696,             # Magic number
    64,                    # Initial checksum value
    0, 1, 14,             # RC4 UA key constants
    md5_params[-2],        # Last 2 bytes of params hash
    md5_params[-1],
    md5_data[-2],         # Last 2 bytes of data hash
    md5_data[-1],
    md5_ua[-2],           # Last 2 bytes of UA hash
    md5_ua[-1]
]

# Add timestamp bytes (big-endian)
salt_list.extend([(timestamp >> i) & 0xFF for i in range(24, -1, -8)])

# Add magic number bytes (big-endian)
salt_list.extend([(536919696 >> i) & 0xFF for i in range(24, -1, -8)])

# Calculate and add checksum
checksum = 64
for x in salt_list[3:]:
    checksum ^= x
salt_list.extend([checksum, 255])
```

**Step 3: Data Filtering and Scrambling**

The salt array undergoes two transformations:

1. **Filtering**: Select 19 bytes in a specific order:
```python
filter_indices = [3,5,7,9,11,13,15,17,19,21,4,6,8,10,12,14,16,18,20]
filtered_list = [salt_list[x-1] for x in filter_indices]
```

2. **Scrambling**: Interleave bytes in a specific pattern:
```python
def scramble(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s):
    return "".join([chr(x) for x in [
        a,k,b,l,c,m,d,n,e,o,f,p,g,q,h,r,i,s,j
    ]])

scrambled = scramble(*filtered_list)
```

**Step 4: Final Encryption and Encoding**

Three final steps create the signature:

1. **RC4 Encryption**: Encrypt scrambled data with simple key:
```python
rc4_result = rc4_encrypt(scrambled, [255])
```

2. **Prefixing**: Add control bytes:
```python
final_data = "\x02\xFF" + rc4_result
```

3. **Custom Base64 Encoding**: Use shifted alphabet:
```python
SHIFT_ARRAY = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe"
signature = b64_encode(final_data, SHIFT_ARRAY)
```

**Complete Signature Generation**
```python
def sign(params: str, ua: str) -> str:
    x_bogus = _x_bogus(params, ua, int(time()))
    return params + "&X-Bogus=" + x_bogus
```

Le résultat est une chaîne encodée en Base64 personnalisée qui doit être ajoutée aux paramètres de la requête avec le préfixe "X-Bogus=".

The output of this final step is the `X-Bogus` signature string.

---

#### **2.2. The X-Argus Signature Algorithm**

The `X-Argus` algorithm is significantly more complex than `X-Bogus`. It involves modern cryptographic primitives, a custom block cipher, and a binary data format (Protocol Buffers) to structure its data.

**Critical Seeds and Constants (v25.1.1)**
```python
DEVICE_REGISTER_SEED = "9e12091dd41b35ef"
DEVICE_VALIDATE_SEED = "dcd12d8b54a31207"
SESSION_SEED = "6f3eefaa51465779"
MAGIC_NUM = "f1b65b6fe1ea6934"
AES_KEY = "afaafa3ada4ada14"
```

**Required Device Parameters**
```python
{
    'device_id': '1234567890123456789',  # Exactly 19 digits
    'install_id': '1234567890123456789',  # Pair that comes with did when registering.
    'device_type': 'SM-G973N',           # Valid Android model
    'os_version': '7.1.2',               # Android version 7+
    'channel': 'googleplay',             # Must be valid channel
    'version_code': '250101',            # Must match app version
    'cpu_abi': 'arm64-v8a',             # Valid CPU architecture
    'build_serial': 'AAAA00000000',      # Valid serial format
    'resolution': '1080x2400',           # Valid device resolution
    'device_brand': 'samsung',           # Matches device_type
    'device_model': 'SM-G973N',          # Must match device_type
    'carrier': 'CMCC',                   # Valid carrier code
    'mcc_mnc': '46000',                  # Matches carrier
    'timezone': 'GMT+08:00'              # Valid timezone
}
```

**Step 1: Data Structuring with Protocol Buffers (Protobuf)**

Instead of a simple list, `X-Argus` organizes its input data into a highly structured object containing over 20 fields, including:
- Device identifiers (`device_id`, `sec_device_id`).
- Application details (`aid`, `version_name`, `sdk_version`).
- The current `timestamp`.
- Cryptographic hashes of the request's query and body.

This object is then serialized using the following Protobuf structure:

```protobuf
message ArgusData {
    string device_id = 1;           // 19-digit device identifier
    string sec_device_id = 2;       // Secondary device ID
    uint32 aid = 3;                 // Application ID 
    string version_code = 4;        // App version code
    string sdk_version = 5;         // SDK version
    uint64 timestamp = 6;           // Current Unix timestamp
    string query_hash = 7;          // SM3 hash of URL parameters
    string body_hash = 8;           // SM3 hash of request body
    string salt = 9;                // Generated from SESSION_SEED
    string leaks = 10;              // Device integrity check
    string cc = 11;                 // Country code
    string tz = 12;                // Timezone offset
    string env_code = 13;           // Environment type
    bytes device_meta = 14;         // Encoded device metadata
    string resolution = 15;         // Screen resolution
    string did_rule = 16;           // Device ID generation rule
    string ap = 17;                // Access point
    string sys = 18;               // System information
    bytes misc = 19;               // Additional metadata
}
```

The order and types of fields must be exact, as TikTok validates the structure.

**Step 2: Hashing the Request Query and Body**

Before being added to the Protobuf structure, the query and body are hashed using the **SM3 cryptographic hash function**. SM3 is a Chinese national standard, similar in purpose to SHA-256, and is significantly stronger than the MD5 algorithm used in `X-Bogus`.

**Step 3: Core Encryption with the Simon Cipher**

This is the cryptographic heart of `X-Argus`. The Simon cipher configuration used is:

```python
SIMON_CONFIG = {
    'block_size': 16,           # 128-bit blocks
    'key_size': 32,            # 256-bit key
    'rounds': 72,              # Number of rounds
    'word_size': 8,           # 64-bit words
    'key_schedule': [         # Constant schedule
        0x9e3779b9,          # sqrt(2) - 2
        0x3c6ef373,          # sqrt(3) - 2
        0x78dde6e6,          # sqrt(5) - 2
        0xf1bbcdcc           # sqrt(7) - 2
    ]
}
```

Implementation steps:
1.  **Padding**: The serialized Protobuf data is padded using PKCS7 to reach a multiple of the block size (16 bytes).
2.  **Key Preparation**: 
    ```python
    def prepare_key(seed):
        key = bytearray(32)
        for i in range(32):
            key[i] = seed[i % len(seed)] ^ ((i * 11) & 0xFF)
        return bytes(key)
    ```
3.  **Simon Encryption**: The data is encrypted block-by-block using the Simon cipher in CBC mode with the following parameters:
    - Block size: 128 bits
    - Key size: 256 bits
    - Number of rounds: 72
    This provides a security level equivalent to AES-256.

**Step 4: Post-Encryption Obfuscation**

The encrypted data from the Simon cipher is further obscured:
1.  **Header Prepending**: A fixed 8-byte header is prepended to the ciphertext.
2.  **Byte Reversal and XORing**: A custom function reverses the byte order of the entire buffer and XORs each byte with a byte from the header, effectively scrambling the ciphertext.
3.  **Final AES Encryption**: The resulting buffer is padded again and then encrypted one last time using the standard **AES cipher** in CBC mode. The AES key and initialization vector (IV) are themselves derived by MD5-hashing parts of another hardcoded key.

**Step 5: Final Formatting**

1.  **Prefixing**: The AES-encrypted data is prefixed with two specific control bytes.
2.  **Base64 Encoding**: The final binary blob is encoded into a standard Base64 string.

This string is the final `X-Argus` signature.

---

### 3. Endpoint Limitations and Operational Challenges

Interacting with the TikTok API, even with valid signatures, is not straightforward. The platform employs a multi-layered defense system that poses significant challenges.

-   **Rate Limiting and IP Reputation**: Aggressive rate limits are in place for all endpoints. An IP address making too many requests in a short period will be temporarily or permanently blocked. The reputation of the IP address (e.g., residential vs. datacenter) also plays a crucial role in the level of scrutiny it receives.

-   **Geographic Restrictions (Geo-fencing)**: Many API endpoints return different content or fail entirely based on the geographical location of the client's IP address. This is fundamental to how TikTok customizes the user experience and enforces regional content policies.

-   **Device and Account Trust Score**: TikTok maintains an internal "trust score" for both devices and user accounts.
    -   **Device Trust**: A newly registered `device_id` is considered untrusted. It must be "warmed up" through a series of activation requests that mimic real user behavior over time. Without a trusted device, many core API calls will return empty data or errors.
    -   **Account Trust**: Accounts that exhibit bot-like behavior (e.g., rapid following, liking, or commenting) are flagged. A flagged account may lose access to certain features or have its API requests systematically denied.

-   **CAPTCHA Challenges**: If the risk control engine detects suspicious activity, it will serve a CAPTCHA challenge. Automated clients must be able to detect these challenges and integrate with a solving service, adding another layer of complexity and cost.

-   **Signature Algorithm Versioning**: The signing algorithms are not static. TikTok frequently pushes updates to the client applications that modify the constants, logic, or entire structure of these algorithms. An implementation that works today may become obsolete overnight, requiring continuous reverse-engineering efforts.

---

### 4. Analysis of Historical API Vulnerabilities

Like any large-scale platform, TikTok's API has had its share of security vulnerabilities in the past. Analyzing these provides insight into potential weak points in complex systems.

-   **Account Takeover via SMS Link Spoofing (2020)**: Researchers discovered a flaw in the `/v1/mobile/verify/` endpoint. By manipulating the request, an attacker could send a fraudulent SMS to a user that appeared to be from TikTok. If the user clicked the link, it allowed the attacker to associate their own phone number with the victim's account, leading to a full account takeover. This highlighted weaknesses in the logic of account recovery and linking mechanisms.

-   **Unauthenticated Information Disclosure (2020)**: Several API endpoints were found to be improperly secured, allowing unauthenticated access to user data such as secondary email addresses, birth dates, and other profile information. This was a classic case of missing authorization checks on sensitive data endpoints.

-   **Deep Link Hijacking and Content Spoofing (2021)**: A vulnerability was identified in how the application handled deep links (`tiktok://`). An attacker could craft a malicious link that, when opened, could force the app to make arbitrary API calls on behalf of the user. This could be used to make a user's private videos public or to display spoofed content within the official app.

-   **Content Processing Vulnerabilities (CVE-2022-28799)**: While not a direct API logic flaw, the way the API handled content uploads presented a significant risk. A vulnerability was found in the third-party media processing library used by TikTok on Android. By uploading a specially crafted video file, an attacker could trigger a memory corruption issue, potentially leading to remote code execution on the user's device. This demonstrates that the attack surface extends beyond the API logic itself to how the platform processes user-submitted data.

These historical examples underscore the immense challenge of securing a platform with such a vast and dynamic API. They show that vulnerabilities can arise not just from cryptographic weaknesses, but also from flawed business logic, improper authorization checks, and insecure handling of user-generated content.

---
### Limitations

Don't think that with these signatures you can takeover TikTok 😂

You will need :

    - **Unflagged and (Real) Accounts/Cookies, you can buy them from me :) for 0.10$/unit if you buy in mass.**

    - **MsTokenEnc and MsTokenDec to generate msToken's, Instead of wasting proxy data on generating while getting page source, you can get it from me (pay).**
