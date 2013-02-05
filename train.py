from pastepm.lib.pyclassifier import Classifier
import os

c = Classifier()

for dirname, dirnames, filenames in os.walk('training'):
    if os.sep not in dirname: continue

    language = dirname.split(os.sep)[1]
    for f in filenames:
        try:
            extension = f.split(".")[1]
        except IndexError:
            extension = f

        full_path = os.path.join(dirname, f)
        c.train(open(full_path).read(), (language, extension))

output = open('training.pckl', 'w+')
c.export(output)
