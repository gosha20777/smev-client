import re

txt = '''<ns6:OriginalMessageId>be76174f-b158-11ea-ac86-3d278eccdb49</ns6:OriginalMessageId>'''

id = re.findall(r'<ns[0-9]:OriginalMessageId>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}</ns[0-9]:OriginalMessageId>', txt)[0]
id = re.findall(r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', id)[0]

print(id)