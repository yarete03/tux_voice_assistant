# **Use voice assistant as Linux service**
⚠️ **Warning:** These instructions should be run with your regular user account on the system (usually the one with UID 1000 in `/etc/passwd`).  
Do **not** run them as `root` or as any user whose UID is lower than 1000, as this process is not intended for those accounts.

You may need to create the following directory if it does not already exist:
~~~ bash
mkdir -p ~/.config/systemd/user/
~~~

Next, copy the provided .service file from your cloned repository to the directory you just created:

**Note:** Replace ${TUX_VOICE_ASSISTANT_PATH} with the path to the cloned repository. 
~~~ bash
mv ${TUX_VOICE_ASSISTANT_PATH}/systemd/voice_assistant.service ~/.config/systemd/user/
~~~

Once the above steps are complete, you can start the service:
~~~ bash
systemctl --user daemon-reload
systemctl --user start voice_assistant.service
~~~

If you want it to launch automatically every time the system boots, you can enable the service:
~~~ bash
systemctl --user enable --now voice_assistant.service
~~~
