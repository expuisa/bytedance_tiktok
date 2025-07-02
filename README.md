# Bytedance TikTok Api
Build your own TikTok Botting solution with our services.
### Explanation

To Avoid Bots on the platform TikTok Added Algorithms Such as X-Argus , X-Gorgon , X-Bogus , X-ladon , X-Tyhon and X-Medusa (More used in Douyin)
These Algorithms was Reverse Engineered on the latest TikTok APK v.40
We can now generate these Algorithms with : 'Device ID' , 'Install ID' , 'Endpoints'
To avoid our API Users having to generate theses our solution provides everything.
每个算法都是独一无二的

### Aftermath

After trying to replicate the same things on the chinese TikTok (抖音) , I have seen that the API Endpoints aren't the same with the global version of TikTok , This means that TikTok Global is an complementary version of Douyin (抖音)
该算法需要安装ID ? 此代码使用我们的第三方 API 生成。我们的解决方案是唯一能够解决验证码、按需请求服务并修改机器人账户信息的解决方案。
Compared with domestic algorithms, the overseas version of tiktok's xg algorithm is actually similar. However, tiktok's risk control measures are earlier and stricter than a certain sound. Most interfaces can be requested directly through the xg algorithm, but core interfaces such as volume, Pay attention, etc., must be used in conjunction with the device registration algorithm
It adds four important parameters, X-Ladon, X-Khronos, X-Gorgon, and X-Argus, to the header of each request. When the URL changes, these parameters will also change.
-

### Endpoints
- Captcha : rc-verification16-normal-no1A.tiktokv.eu , api16-normal-no1a.tiktokv.eu
- Proxyless Endpoints : useast5 , maliva , useast1a , useast8
### Scheme

- Find Endpoint -> Generate Algo -> Do request and Send Key -> OK
- Find Endpoint -> Do request -> NO Authorization or Parameter Error

### Finding Endpoints

Launch MEMU Emulator + HTTP Toolkit

Create a new virtual Android device.
In the settings, enable "Root Device"
Start Emulator then install the TikTok Apk to it

In HTTP Toolkit, and in Intercept tab , select "Android Device via ADB".

Open Tiktok & The View tab in HTTP Toolkit to view all requests.

### (Argus) Sign Keys - 签名密钥
- sign_key : \xac\x1a\xda\xae\x95\xa7\xaf\x94\xa5\x11J\xb3\xb3\xa9}\xd8\x00P\xaa\n91L@R\x8c\xae\xc9RV\xc2\x8c
- sm3 : \xfcx\xe0\xa9ez\x0ct\x8c\xe5\x15Y\x90<\xcf\x03Q\x0eQ\xd3\xcf\xf22\xd7\x13C\xe8\x8a2\x1cS\x04
/!\ We get an Argus that is very short!

### Important

The scripts i've released was especially made for Douyin but IT will work with Global/US TikTok. (Nearly Same Algorithms -> X-A X-G X-L X-M X-T X-B

### Tree Possible Actions

- UserInteractions
  - FollowUser (Needs unflagged HQ Account)
  - LikePost
  - CommentPost
  - WatchVideo (Only on some endpoints)
  - LikePostComment
  - SaveVideo
  - ShareVideo
  - PrivateMessageUser
  - GetUserFeed (Unflaggs Account after using it after actions)
- TikTokShopInteractions
  - Get Product Price
  - Report Item
  - Get Product Info
  - Get Product Images
- DeviceInteractions
  - SendView/WatchVideo (Doesn't count in monetization) (Account needs depends on endpoint)
  - FullyWatchVideo (Unavailable and Takes time)
  - Report User
  - RegisterDevice
- UserInteractions (Only Douyin)
  - SendUserFavorite
- Logins
  - GetCodeViaMobile (Douyin only)
  - GetCodeViaMobile (Douyin only)
  - RegisterAccont (Not Working?)
  - LoginAccount (SessionID only)


