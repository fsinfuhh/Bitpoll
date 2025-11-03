# बिटपोल (Bitpoll)
बिटपोल एक सॉफ़्टवेयर है जो तारीख़ों, समय या सामान्य प्रश्नों पर पोल (मतदान) आयोजित करने के लिए बनाया गया है।
यह opatuit के Dudel (https://github.com/opatut/dudel) का एक नया संस्करण है, जो https://bitpoll.de पर उपयोग किया गया है, और इसे Django फ़्रेमवर्क का उपयोग करके पुनर्लिखित किया गया है।
## Docker का उपयोग
डॉकर इमेज वर्तमान मास्टर ब्रांच से स्वचालित रूप से बनाई जाती है।  
आप डॉकर कंटेनर सेटअप करने के लिए निम्नलिखित कमांड्स का उपयोग कर सकते हैं।
### स्टैटिक और कॉन्फ़िग फ़ाइलों के लिए एक डायरेक्टरी बनाएँ:
```bash
mkdir -p run/{log,static,config}
```

### उदाहरण सेटिंग्स फ़ाइल प्राप्त करें और अपनी आवश्यकताओं के अनुसार इसे अनुकूलित करें:
```bash
wget https://raw.githubusercontent.com/fsinfuhh/Bitpoll/master/bitpoll/settings_local.sample.py -O run/config/settings.py
```


### यह महत्वपूर्ण है कि आप कम से कम डेटाबेस सेटिंग्स, सीक्रेट की और अलाउड होस्ट्स को बदलें।  
### डॉकर कंटेनर प्रारंभ करें:
```bash
docker run -a stdout -a stderr --rm --name bitpoll -p 3008:3008 -p 3009:3009 --volume ./run/static:/opt/static --volume ./run/config:/opt/config ghcr.io/fsinfuhh/bitpoll
```
कंटेनर पोर्ट 3009 पर उपलब्ध है।
यदि आप किसी बाहरी वेब सर्वर का उपयोग करते हैं, तो आप पोर्ट 3008 पर uwsgi ट्रैफ़िक को अग्रेषित कर सकते हैं और run/static से static तक स्थिर संसाधन प्रदान कर सकते हैं।  

## मैनुअल इंस्टॉल
कोड प्राप्त करें:
```bash
git clone https://github.com/fsinfuhh/Bitpoll
```

## Python वर्चुअलएन्व (virtualenv) बनाएं और डिपेंडेंसीज़ इंस्टॉल करें
```bash
virtualenv -p $(which python3) .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt
```

bitpoll/settings_local.sample.py को bitpoll/settings_local.py में कॉपी करें और स्थानीय सेटिंग्स को अनुकूलित करें।
### डेटाबेस प्रारंभ करें:
```bash
./manage.py migrate
```

### टेस्ट सर्वर चलाएँ:
```bash
./manage.py runserver
```

## प्रोडक्शन (Production)
प्रोडक्शन में त्रुटि रिपोर्टिंग (error reporting) के लिए *Sentry* का उपयोग किया जाता है।  
*django-auth-ldap* का उपयोग LDAP के माध्यम से लॉगिन के लिए किया जाता है।  
*uWSGI* का उपयोग ऐप को सर्व करने के लिए किया जाता है।

### प्रोडक्शन के लिए डिपेंडेंसीज़ इंस्टॉल करें:
```bash
sudo apt install g++ make python3-psycopg2 python3-ldap3 gettext gcc python3-dev libldap2-dev libsasl2-dev
```

### Python डिपेंडेंसीज़ इंस्टॉल करें:
```bash
pip install -r requirements-production.txt
```

कॉन्फ़िगरेशन उदाहरण settings_local.py में दिए गए हैं।
हमारा उपयोग किया गया uWSGI कॉन्फ़िग यहाँ पाया जा सकता है:  
<https://github.com/fsinfuhh/mafiasi-rkt/blob/master/bitpoll/uwsgi-bitpoll.ini>

### प्रोडक्शन सिस्टम्स के लिए निम्नलिखित चलाना आवश्यक है:
```bash
./manage.py compilemessages
./manage.py collectstatic
```

## डिपेंडेंसीज़ का प्रबंधन (Management of Dependencies)
हम डिपेंडेंसीज़ को प्रबंधित करने के लिए *pip-tools* का उपयोग करते हैं।  
requirements*.in फ़ाइलों में किसी संशोधन या पैकेजों के अपडेट के बाद निम्नलिखित कमांड चलाएँ:
```bash
pip-compile --upgrade --output-file requirements.txt requirements.in
pip-compile --upgrade --output-file requirements-production.txt  requirements-production.in requirements.in
```

अपना वातावरण (environment) requirements.txt के साथ सिंक करने के लिए यह कमांड चलाएँ:
```bash
pip-sync
```

यह वर्चुअलएन्व में आवश्यक डिपेंडेंसीज़ को इंस्टॉल या डिइंस्टॉल करेगा ताकि यह requirements फ़ाइल से मेल खा सके।
