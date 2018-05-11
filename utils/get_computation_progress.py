#!/usr/bin/env python
import os
import sys
import re
import subprocess


def _output_shell(line):
  try:
    shell_command = subprocess.Popen(line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  except OSError:
    return None
  except ValueError:
    return None

  (output, err) = shell_command.communicate()
  shell_command.wait()
  if shell_command.returncode != 0:
    print("Shell command failed to execute")
    return None

  return output

def get_progress(cache_folder, intermediate=False):
    walk_dir = cache_folder
    computed_length = 0
    total_length = 0
    total_compar = 0
    #out_file = sys.argv[2]
    #f = open(out_file,'w')

    for root, subdirs, files in os.walk(walk_dir):
        if files:
        #print(root+"\n")
        part = re.split("\_|-|\.",files[0])
        if part[0] == "part":
            gzip_files = int(_output_shell("ls " + os.path.abspath(root) + "/*.gz | wc -l"))
            ckpt_files = int(_output_shell("ls  " + os.path.abspath(root) + "/*.ckpt | wc -l"))
            all_files = int(_output_shell("ls " + os.path.abspath(root) + "/* | wc -l"))
            in_progress_files = float(all_files - gzip_files - ckpt_files)/float(part[len(part)-2])*100
            computed_length += gzip_files
            total_compar += 1
            total_length += int(part[len(part)-2])
            individual_progress = float(gzip_files)/float(part[len(part)-2])*100
            ckpt_progress = float(ckpt_files)//float(part[len(part)-2])*100
            if intermediate:
                print("--- Progress of {} vs {}---".format(root.split("/")[-1], root.split("/")[-2]))
                print("Individual Progress: {}".format(round(individual_progress,2)))
                print("Checkpoints: {}".format(round(ckpt_progress,2)))
                print("Currently unfinished: {}".format(round(in_progress_files,2)))
    
    return (computed_length, total_length, total_compar)


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:i:h", ["cache_folder=", "intermediate="])
    except getopt.GetoptError as e:
        print(str(e))
        print('get_computation_progress.py -c <cache all vs all folder> -i <print intermediate>')
        sys.exit(2)

    cache_folder = None
    intermediate = False

    for opt, arg in opts:
        if opt == '-h':
            print('get_computation_progress.py -c <cache all vs all folder> -i <print intermediate>')
            sys.exit()
        elif opt in ("-c", "--cache_folder"):
            cache_folder = arg
            if cache_folder[-1] is not "/":
                cache_folder += "/"
        elif opt in ("-i", "--intermediate"):
            intermediate = arg
        else:
            assert False, "unhandled option"

    computed_length, total_length, total_compar = get_progress(cache_folder, intermediate=intermediate)
    t_progress = 100*float(computed_length)/float(total_length)
    print("Computed Files: " +str(computed_length)+ "/" +str(total_length)+ "\n")
    print("Total Progress: " +str(round(t_progress,2))+ "%\n")
    print("Total All vs All comparisons: " +str(total_compar))

if __name__ == "__main__":
    main()

