Bitpoll

Bitpoll అనేది తేదీలు, సమయాలు లేదా సాధారణ ప్రశ్నలపై ఓటింగ్ (polls) నిర్వహించడానికి ఉపయోగించే సాఫ్ట్‌వేర్.
ఇది Dudel (https://github.com/opatut/dudel) అనే సాఫ్ట్‌వేర్ యొక్క కొత్త వెర్షన్, ఇది Django framework ఉపయోగించి తిరిగి వ్రాయబడింది.


---

🐳 Docker ఉపయోగించడం

Docker image ప్రస్తుత master branch నుండి ఆటోమేటిక్‌గా నిర్మించబడుతుంది.
క్రింది కమాండ్లను ఉపయోగించి docker కంటైనర్ సెట్ చేయవచ్చు:

1️⃣ Static మరియు Config ఫైళ్ల కోసం ఫోల్డర్ సృష్టించండి:

mkdir -p run/{log,static,config}

2️⃣ ఉదాహరణ Settings ఫైల్ పొందండి మరియు మీ అవసరాలకు అనుగుణంగా సవరించండి:

wget https://raw.githubusercontent.com/fsinfuhh/bitpoll/master/bitpoll/settings_local.sample.py -O run/config/settings.py

⚠️ గమనిక: డేటాబేస్ సెట్టింగ్స్, సీక్రెట్ కీ, మరియు allowed hosts తప్పనిసరిగా మార్చాలి.

3️⃣ Docker కంటైనర్ ప్రారంభించండి:

docker run -a stdout -a stderr --rm --name bitpoll -p 3008:3008 -p 3009:3009 --volume ./run/static:/opt/static --volume ./run/config:/opt/config ghcr.io/fsinfuhh/bitpoll

కంటైనర్ port 3009 లో అందుబాటులో ఉంటుంది.
మీరు బాహ్య వెబ్ సర్వర్ ఉపయోగిస్తే, port 3008 పై uwsgi ట్రాఫిక్ ఉపయోగించి, static ఫైళ్లను /static/ వద్ద అందించవచ్చు.


---

⚙️ మాన్యువల్ ఇన్‌స్టలేషన్ (Manual Install)

1️⃣ కోడ్‌ను పొందండి:

git clone https://github.com/fsinfuhh/Bitpoll

2️⃣ Python virtualenv సృష్టించి అవసరమైన dependencies ఇన్‌స్టాల్ చేయండి:

virtualenv -p $(which python3) .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt

3️⃣ ఉదాహరణ సెట్టింగ్స్ కాపీ చేయండి:

cp bitpoll/settings_local.sample.py bitpoll/settings_local.py

తర్వాత మీ అవసరాలకు అనుగుణంగా సవరించండి.

4️⃣ డేటాబేస్ ప్రారంభించండి:

./manage.py migrate

5️⃣ టెస్ట్ సర్వర్ నడపండి:

./manage.py runserver


---

🚀 Production సెటప్

Production లో:

Sentry – error reporting కోసం

django-auth-ldap – LDAP login కోసం

uwsgi – app సర్వ్ చేయడానికి ఉపయోగిస్తారు


అవసరమైన Dependencies ఇన్‌స్టాల్ చేయండి:

sudo apt install g++ make python3-psycopg2 python3-ldap3 gettext gcc python3-dev libldap2-dev libsasl2-dev

Python dependencies ఇన్‌స్టాల్ చేయండి:

pip install -r requirements-production.txt

సెట్టింగ్స్ మార్చడానికి:

settings_local.py ఫైల్‌లో మార్పులు చేయండి.

uWSGI కాన్ఫిగరేషన్ ఉదాహరణ:

https://github.com/fsinfuhh/mafiast-rkt/blob/master/bitpoll/uwsgi-bitpoll.ini

Production సిస్టంలో ఈ కమాండ్లు తప్పనిసరిగా అమలు చేయాలి:

./manage.py compilemessages
./manage.py collectstatic


---

📦 Dependencies నిర్వహణ (Management of Dependencies)

మేము pip-tools ను డిపెండెన్సీలను నిర్వహించడానికి ఉపయోగిస్తాము.
ప్యాకేజీలను మార్చిన తర్వాత లేదా అప్‌డేట్ చేసిన తర్వాత ఈ కమాండ్లు నడపండి:

pip-compile --upgrade --output-file requirements.txt requirements.in
pip-compile --upgrade --output-file requirements-production.txt requirements-production.in

తర్వాత ఎన్విరాన్‌మెంట్‌ను requirements.txt తో సింక్ చేయడానికి:

pip-sync

ఇది మీ virtualenv ను తాజా ప్యాకేజీలతో సరిపోల్చి అవసరమైన వాటిని ఇన్‌స్టాల్ లేదా తొలగిస్తుంది.


---


