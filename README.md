# MUNI Thesis Notifier
Get notified when there is a new bachelor thesis available!

## Requirements
All you should need to run this is `python3`. I have tested this only on linux machines, but I don't believe there would be any problems running this on any other OS.

Also you should have installed some basic tools like `git` and `virtualenv` on your machine.

## How to install
### Clone this repository and change directory
```bash
git clone https://github.com/fstavela/fi-muni-thesis-notifier.git
cd fi-muni-thesis-notifier
```

### Create virtual environment and activate it
```bash
virtualenv -p python3 venv
source venv/bin/activate
```

### Install python dependencies
```bash
pip install -r requirements.txt
```

### Edit settings
You can either create new file called `settings.local.yaml` (copied from `settings.yaml`) where you can put your settings/credentials or you can edit existing `settings.yaml`.

If you want to use a gmail account to send you notifications, you can leave `port` and `smtp_server` settings. Otherwise adjust these settings to your email service.

If you are using gmail (and most probably also other email services), you will also have to allow "Less secure app access" settings to your account. You can read more [here](https://support.google.com/accounts/answer/6010255)

### Run it
```bash
python3 main.py
```
Optionally you can run it in the background, so you can log out of your machine without killing the process
```bash
nohup python3 main.py &
```

## Warning
Email texts are written in Slovak language. They include some funny Slovak swearing phrases which were mostly used by legendary Ladislav Meliško. They are there just for fun and they are not meant to offend anybody.

## Additional information
This tool is meant to notify you when someone adds a new bachelor thesis to MUNI IS, but it should be pretty simple to adjust it to also work with master thesis. If you came so far that you want to start working on a bachelor thesis, I expect that you have enough programming experience to be able to do this simple task yourself. At least if you are from Faculty of Informatics. If not, well... not my problem :trollface:
