# Bytedance TikTok Api

### Explanation

Pour éviter les bots sur la plateforme TikTok, ont ajouté des algorithms comme X-Argus , X-Gorgon , X-Bogus , X-Ladon , X-Typhon et X-Medusa (sont plus ultilisés dans la version chinoise de TikTok)
Ces algorithmes ont été Reversé sur la dernière version android de TikTok.
Nous pouvons générer et ultiliser ces algorithmes.


To Avoid Bots on the platform TikTok Added Algorithms Such as X-Argus , X-Gorgon , X-Bogus , X-ladon , X-Tyhon and X-Medusa (More used in Douyin)
These Algorithms was Reverse Engineered on the latest TikTok Android App
We can now generate these Algorithms with : 'Device ID' , 'Install ID' , 'Endpoints'
每个算法都是独一无二的

### Aftermath
Après avoir essayé de Répliquer les mêmes choses dans de différents TikTok (Chinoises) , J'ai vu que les Endpoints des API n'étaient pas la même avec le version Global de TikTok, ça veut dire que TikTok Globale est une version complémentaire de Douyin (TT Chinoise)
Comparé avec des algorithmes domestiques, La version étrangère de l'algorithme xg de TikTok est actuellement similaire, Mais, le contrôle de risque de TikTok est en avant et est plus strict d'un autre son. La plupart des requêtes peuvent être demandés directement depuis l'algorithme x-g , mais des interfaces coeurs et etc.. Doivent être ultilisés avec l'algorithme du Simulation d'Appareils.
Il ajoute quatre paramètres importantes, X-Ladon, X-Khronos, X-Gorgon et X-Argus, dans la tête de chaque requête, si le URL change , ces paramêtres/algorithme vont changer.
- X-Khronos est simplement le temps générale du serveur en Unix
-  X-Gorgon , X-Bogus , X-Argus , X-Medusa , X-Thyron et X-Ladon , dans l'autre main est une signature de sécurité ultilisé dans les requêtes de l'Api TikTok, générés depuis des séries sophistiqués des opérations cryptographiques.

Le processus commence par le calcul des hachages MD5 des composants clés de la requête, notamment les paramètres d'URL, le corps de la requête (souvent appelé « stub ») et les cookies. Ces hachages sont combinés dans un tableau initial, avec certaines valeurs constantes et l'heure Unix actuelle.

Ce tableau est ensuite traité par un moteur de transformation personnalisé, généralement appelé classe XG. Chaque élément subit des opérations bit à bit complexes, notamment l'inversion de bits, le XOR avec des valeurs fixes et calculées, et la rotation de bits. Des fonctions comme reverse et RBIT sont utilisées pour masquer davantage les données.

L'algorithme transforme le tableau de manière itérative, en appliquant des couches de logique au niveau du bit afin de garantir que chaque signature est unique et difficile à reproduire. Le résultat final est une chaîne hexadécimale, préfixée par « 8402 », qui constitue l'en-tête X-Gorgon.

Cette signature sert de preuve cryptographique de l'authenticité de la requête et de son intégrité, permettant à TikTok de valider les requêtes et de protéger son API contre les accès non autorisés ou les falsifications.
-


After trying to replicate the same things on the chinese TikTok (抖音) , I have seen that the API Endpoints aren't the same with the global version of TikTok , This means that TikTok Global is an complementary version of Douyin (抖音)
该算法需要安装ID ? 此代码使用我们的第三方 API 生成。我们的解决方案是唯一能够解决验证码、按需请求服务并修改机器人账户信息的解决方案。
Compared with domestic algorithms, the overseas version of tiktok's xg algorithm is actually similar. However, tiktok's risk control measures are earlier and stricter than a certain sound. Most requests can be requested directly through the xg algorithm, but core interfaces etc., must be used in conjunction with the device registration algorithm
It adds four important parameters, X-Ladon, X-Khronos, X-Gorgon, and X-Argus, to the header of each request. When the URL changes, these parameters will also change.
- X-Khronos is simply the current Unix server timestamp.
- X-Gorgon , X-Bogus , X-Argus , X-Medusa , X-Thyron and X-Ladon , on the other hand, is a security signature used in TikTok API requests, generated through a sophisticated series of cryptographic operations.

The process begins by computing MD5 hashes of key components of the request—this includes the URL parameters, request body (often referred to as the "stub"), and any cookies. These hashes are combined into an initial array along with certain constant values and the current Unix time.

This array is then processed by a custom transformation engine, typically referred to as the XG class. Each element undergoes complex bitwise operations, including bit reversal, XOR with both fixed and calculated values, and bit rotations. Functions like reverse and RBIT are used to further obscure the data.

The algorithm iteratively transforms the array, applying layers of bit-level logic to ensure that each signature is unique and difficult to replicate. The final output is a hexadecimal string, prefixed with '8402', which forms the X-Gorgon header.

This signature serves as a cryptographic proof that the request is authentic and has not been altered, helping TikTok validate requests and protect its API from unauthorized access or tampering.
-

### Endpoints
- Captcha : rc-verification16-normal-no1A.tiktokv.eu , api16-normal-no1a.tiktokv.eu
- Proxyless Endpoints : useast5 , maliva , useast1a , useast8
### Scheme

- Find Endpoint -> Generate Algo -> Do request and Send Key -> OK
- Find Endpoint -> Do request -> NO Authorization or Parameter Error

- Trouver l'endpoint -> Générer l'Algo -> Faire une requête et envoyer les clés -> OK
- Trouver l'endpoint -> Faire une requête -> PAS D'autorisation ou Erreur de paramètres.

### Finding Endpoints

Launch MEMU Emulator + HTTP Toolkit

Create a new virtual Android device.
In the settings, enable "Root Device"
Start Emulator then install the TikTok Apk to it

In HTTP Toolkit, and in Intercept tab , select "Android Device via ADB".

Open Tiktok & The View tab in HTTP Toolkit to view all requests.

### Douyin Device Registration

After testing, it was found that TikTok's device registration is not a single request can be completed, although the simulated request obtains device_id and install_id, but if you use the newly obtained device information to access the encrypted interface, you will get an empty response. Check the information and learn that there is a follow-up activation request. (Cause: No algorithms) I've found that a single mock request was not enough to fully mimic the behavior of a real device. The real breakthrough lies in a series of subsequent "activation" requests, which makes the generated device information closer to the real device environment, thus avoiding the risk of being identified by the platform because the information is too single or false

### (Argus) Sign Keys - 签名密钥
- sign_key : \xac\x1a\xda\xae\x95\xa7\xaf\x94\xa5\x11J\xb3\xb3\xa9}\xd8\x00P\xaa\n91L@R\x8c\xae\xc9RV\xc2\x8c
- sm3 : \xfcx\xe0\xa9ez\x0ct\x8c\xe5\x15Y\x90<\xcf\x03Q\x0eQ\xd3\xcf\xf22\xd7\x13C\xe8\x8a2\x1cS\x04
/!\ We get an Argus that is very short and can be Invalid
/!\ Nous avons un algorithme X-Argus qui est vraiment petit ce qui montre qu'il est invalide.

Cependant ceci est à revoir dans le fichier que j'ai partagé.

### Important
**Les scripts que j'ai partagé sont espéciallement fait pour Douyin (Version chinoise de TikTok) mais IL va marcher avec la version Global/Américaine de TikTok.**
Les scripts doivent marcher mais vous devez le modifier à vos besoins.


The scripts i've released was especially made for Douyin but IT will work with Global/US TikTok. (Nearly Same Algorithms -> X-A X-G X-L X-M X-T X-B)
Most of the scripts should work but you will need to modify to your likings.
我手头的大部分剧本都是一年前或更久以前的。

### Tree Possible Actions / Actions possibles

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
  - RegisterAccont (Working but really flagged)
  - LoginAccount (SessionID only)


