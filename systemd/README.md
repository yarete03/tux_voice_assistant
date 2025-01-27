# **Use voice assistant as Linux service**

You should create the following directory path if it is not already created:

~~~ bash
mkdir -p ~/.config/systemd/user/
~~~

Next you should copy the provided .service file on this folder to the directory we just tried to create:

⚠️ **Note:** You should change the ${TUX_VOICE_ASSISTANT_PATH} variable with the path that contains the git cloned repo.
~~~ bash
mv ${TUX_VOICE_ASSISTANT_PATH}/systemd/voice_assistant.service ~/.config/systemd/user/
~~~

Once we've finished with previous steps, we can launch our service:
~~~ bash
systemctl --user daemon-reload
systemctl --user start voice_assistant.service
~~~

If you want it to be launched every time the PC is booted, you can enable the service:
~~~ bash
systemctl --user enable --now voice_assistant.service
~~~
