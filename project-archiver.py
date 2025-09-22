#  analyse project
#  move projec files except videos
#  compress all video files to new location
#  compare both projects locations old and archived

from pathlib import Path
import logging
import magic # pip install python-magic
import os
from dataclasses import dataclass
from datetime import date

# project-archiver.py location
PWD = Path(__file__).parent.resolve()
logger = logging.getLogger(__name__)
logging.basicConfig(filename=Path(PWD,'project-archiver.log'), encoding='utf-8', level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# define users home directory
home = str(Path.home())
# video input files (current directory)
video_input_directory = Path.cwd()
# video output directory
video_output_directory = Path(home,'Desktop', 'archived_projects')
Path(video_output_directory).mkdir(parents=True, exist_ok=True)

@dataclass
class Project():
    name: str
    #age: date
    size: str
    videos: int
    nonvideos: int

    def total_files(self) -> int:
        return self.videos + self.nonvideos

project = Project(name='', size=0, videos=0, nonvideos=0)


# test if file is a video
def test_mimetype(file):
    mime = magic.Magic(mime=True)
    return mime.from_file(file)

def rsync_project_files(directory):
    file_count, dir_count, video_count = 0,0,0
    for root, dirs, files in os.walk(directory):
        dir_count += len(dirs)
        file_count += len(files)
        for file in files:
            mimetype = test_mimetype(Path(root,file))
            if mimetype.startswith("video"):
                print(Path(root,file))
                print(mimetype)
                project.videos = project.videos + 1
                pass
            else:
                print(Path(video_output_directory,root,file))
                print(mimetype)
                project.nonvideos = project.nonvideos + 1
                #subprocess.call(['rsync', '-av', Path(root,file), Path(video_output_directory,root,file)])


def main(video_input_directory=video_input_directory):
    rsync_project_files(video_input_directory)
    #statistics(video_input_directory)
    #statistics(video_output_directory)
    print(project, project.total_files())

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source_directory")
    parser.add_argument("-d", "--destination_directory")
    args = parser.parse_args()
    
    #logger.info('started:')

    if args.source_directory:
        main(video_input_directory= args.source_directory)
    else:
        main(video_input_directory = video_input_directory)
    