#automating the process

from voiceToText import generateText  #generates generatedFile.txt
from summary import create_summary_file     #generates summary.txt

generateText()
create_summary_file()

print("\nsummary produced")