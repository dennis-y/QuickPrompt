from PyQt5.QtCore import QSettings, QStandardPaths
import tomlkit
from fuzzywuzzy import process
import os
import json

import logging
logger = logging.getLogger(__name__)


def build_defaults():
    doc = tomlkit.document()

    def comment(message):
        doc.add(tomlkit.comment(message))
    def nl():
        doc.add(tomlkit.nl())
    def multi(s):
        return tomlkit.string(s, multiline=True, literal=True)
    def prompt(name, template):
        return {'name': name, 'template': multi(template)}
    
    # How to make the iteration easier here?
    # maybe default.toml, then user.toml?
    
    comment('This is the list of supported LLM providers.')
    comment('Add the API keys for the ones you would like to use.')

    doc['providers'] = [
        {'name': 'openai', 'api_key': ''},
        {'name': 'mistral', 'api_key': ''},
    ]

    nl()
    nl()
    comment('These are the built in prompt templates. Feel free to edit or add your own.')
    doc['prompts'] = [
        prompt('Blank', ''),
        prompt('Universal Dictionary', '''
Please explain any challenging or unusual terms in the following passage. 
YOU MUST respond using the same language as the one that the foreign passage is written in.
Passage:
{clipboard}
'''),
        prompt('Gloss', '''
Provide a glossing for the following passage into English.
Do this phrase by phrase, by first reproducing the phrase in the original language,
then adding the english literal translation in parenthesis, then the next phrase
in the original language, et cetera.

The passage:
{clipboard}
'''),
        prompt('Translate to English', '''
Translate the following passage to english:
{clipboard}
'''),
        prompt('Summarize', '''
You are an expert at making text more concise without changing its meaning. Don't reword, don't improve. 
Just find ways to combine and shorten the text. Use lists when appropriate. 

Here is the text to be summarized:
{clipboard}
'''),
    ]
    return doc


def build_user_config_default():
    doc = tomlkit.document()

    def comment(message):
        doc.add(tomlkit.comment(message))

    comment('This is the list of supported LLM providers.')
    comment('Add the API keys for the ones you would like to use.')

    doc['providers'] = [
        {'name': 'openai', 'api_key': ''},
        {'name': 'mistral', 'api_key': ''},
    ]
    return doc


class QSettingsWrapper:
    def __init__(self) -> None:
        self.qsettings = QSettings("MyCompany", "MyApp")
        self.num_recent_prompts = self.qsettings.value("numRecentPrompts", 50)
        self.prompts = {}
        self.ordered_prompt_names = []
        config = self.load_config()
        self.api_keys = {}
        for provider in config['providers']:
            self.api_keys[provider['name']] = provider['api_key']
        for prompt in config['prompts']:
            self.prompts[prompt['name']] = prompt
            self.ordered_prompt_names.append(prompt['name'])

    def read_config_file(self, name):
        appConfigPath = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        fullPath = os.path.join(appConfigPath, name)
        logger.info(f'Read config file from {fullPath}')
        if not os.path.exists(fullPath):
            logger.info('File not found')
            return None
        with open(fullPath, 'r') as f:
            return tomlkit.load(f)

    def write_config_file(self, name, data):
        appConfigPath = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        fullPath = os.path.join(appConfigPath, name)
        logger.info(f'Write config file to {fullPath}')
        with open(fullPath, 'w') as f:
            return tomlkit.dump(data, f)
        
    def load_config(self):
        system_config_name = 'quickprompt_system.toml'
        user_config_name = 'quickprompt_user.toml'

        config = build_defaults()
        self.write_config_file(system_config_name, config)

        user_config = self.read_config_file(user_config_name)
        if user_config is None:
            logger.info(f'User config not found, creating default')
            user_config = build_user_config_default()
            self.write_config_file(user_config_name, user_config)
    
        logger.info(f'Updating default config with user config')
        config.update(user_config)

        return config
    
    def get_api_key(self, service):
        return self.api_keys[service]

    def selectPrompt(self, name):
        # Update MRU commands list
        mruCommands = self.qsettings.value("mruCommands", [])
        if name in mruCommands:
            mruCommands.remove(name)
        mruCommands.insert(0, name)
        truncated = mruCommands[:self.num_recent_prompts]
        self.qsettings.setValue("mruCommands", truncated)

    def getTemplateForPromptNamed(self, name):
        if name not in self.prompts:
            return ''
        return self.prompts[name]['template']

    def getMostRecentPromptName(self):
        result = self.getMostRecentPromptNames(1)[0]
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
        
        for name in self.ordered_prompt_names:
            if name in mruCommands:
                continue
            mruCommands.append(name)
            if len(mruCommands) >= num:
                break
        
        logger.info(f'recent commands: {mruCommands}')
        return mruCommands
        
    def getMatchingPromptNames(self, text):
        return process.extract(text, self.ordered_prompt_names, limit=self.num_recent_prompts)


settings = QSettingsWrapper()



