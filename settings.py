from PyQt5.QtCore import QSettings
import tomlkit
from fuzzywuzzy import process


class QSettingsWrapper:
    def __init__(self) -> None:
        self.qsettings = QSettings("MyCompany", "MyApp")
        self.num_recent_prompts = self.qsettings.value("numRecentPrompts", 6)
        print(f'num most recent: {self.num_recent_prompts}')
        self.prompts = {}
        with open('prompts.toml', 'r') as f:
            for prompt in tomlkit.parse(f.read())['prompts']:
                print(prompt)
                self.prompts[prompt['name']] = prompt
        self.sorted_prompt_names = sorted(list(self.prompts.keys()))
        existing = self.qsettings.value("mruCommands", [])
        print(f'existing mru = {existing}')
    
    def selectPrompt(self, name):
        # Update MRU commands list
        mruCommands = self.qsettings.value("mruCommands", [])
        print(f'existing = {mruCommands}')
        if name in mruCommands:
            mruCommands.remove(name)
        mruCommands.insert(0, name)
        truncated = mruCommands[:self.num_recent_prompts]
        self.qsettings.setValue("mruCommands", truncated)
        print('did update mru commands')
        print(f'new commands = {truncated}')
        
    def getTemplateForPromptNamed(self, name):
        if name not in self.prompts:
            return ''
        return self.prompts[name]['template']

    def getMostRecentPromptName(self):
        result = self.getMostRecentPromptNames(1)[0]
        print(f'most recent prompt {result}')
        return result

    def getMostRecentPromptNames(self, num=None):
        if num is None:
            num = self.num_recent_prompts
        mruCommands = []
        # Skip prompts that were deleted/renamed
        for name in self.qsettings.value("mruCommands", []):
            if name in self.prompts:
                mruCommands.append(name)

        if len(mruCommands) >= num:
            return mruCommands[:num]
        
        for name in self.sorted_prompt_names:
            if name in mruCommands:
                continue
            mruCommands.append(name)
            if len(mruCommands) >= num:
                break
        
        print(f'recent commands: {mruCommands}')
        return mruCommands
        
    def getMatchingPromptNames(self, text):
        return process.extract(text, self.sorted_prompt_names, limit=self.num_recent_prompts)


settings = QSettingsWrapper()
