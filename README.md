
TODO:

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
