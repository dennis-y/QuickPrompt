
TODO:

release
- [ ] settings: some way to edit+save them all in qsettings (no conf files)
    - [ ] maybe qsettings read first, then overwritten with $HOME/settings later on. 
    - we can use QStandardPaths for this
- [ ] settings: api key
- [ ] settings: model
- [ ] settings default model
- [ ] (optional) model per-prompt, or some other way to change model in ui
- [ ] UI: show the model being used 
- [ ] packaging: Make the outputs not overwrite each other. Some way to do github packages + releases here? 

settings ideas:
- how to make this work for both dev and shipping?
- maybe a defaults.py that gets loaded on first run, then written out to the standard config
  location if it doesn't exist? (Otherwise, the config there is loaded + merged in)

quick
- [ ] Readme description of project
- [ ] Use flex layout instead of hardcoding pixels
- [ ] Move templates to external file. Is there a standard prompt format?
- [x] send message history. (But don't show in the UI)
- [ ] set company + app name
- [x] env variable to clear settings OR default get blank for missing

not so quick
- [x] gracefully handle renamed/deleted commands
- [ ] better error handling when network is down
- [ ] Readme demo video
- [ ] Add more prompts
- [ ] Make the UI prettier
- [x] github action for build on linux
- [ ] action for build on mac
- [ ] try installing on mac
- [x] common wrapper around openai, mistral
- [ ] UI for settings. just api key for now.
- [x] reduce file size from 500MB. mistralai requires pyarrow which is 150+MB. replace with HTTP calls. 575 -> 236, 88MB compressed
