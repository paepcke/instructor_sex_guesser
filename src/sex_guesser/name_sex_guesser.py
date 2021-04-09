'''
Created on Apr 8, 2021

@author: paepcke
'''
from _ast import arg
import argparse
import csv
import os
import sys


class NameSexGuesser:
    '''
    Combines a list of English first names with 
    a list of last/first[/middle-initial] entries.
    Outputs a .csv last,first,middle-initial,<sex>
    where sex in {M,F,U}. A 'U' stands for unknown,
    and occurs when the given baby list does not have
    an entry for the first name.
    
    Optionally, creates an additional file with a 
    list of the unknown entries.
    '''

    #------------------------------------
    # Constructor 
    #-------------------


    def __init__(self, 
                 instructor_names_file, 
                 baby_names_file,
                 outfile=None,
                 unknowns_dest=None
                 ):
        '''
        Given single column file like:
        
		   instructors
		   Aaker, Jennifer L
		   Aaker, Jennifer L
		   Aaker, Jennifer L; Li, Fei-Fei
		   Aalami, Oliver O
		   Aalami, Oliver O; Yock, Paul
		   Aanjaneya, Mridul
		   Aaronson Wright, Cassiana
		   Aaronson Wright, Cassiana

        create a list of InstructorName instances.
        
        Also given a baby names file like:
        
          Florence,F,1063
          Cora,F,1045
          Martha,F,1040
          Laura,F,1012
        
        Read the baby_names_file, and create a dict
             name --> sex 
        
        @param instructor_names_file: file with names of instructors
        @type instructor_names_file: str
        @param baby_names_file: file of baby names
        @type baby_names_file: str
        @param outfile: optional destination path for result. Default: stdout
        @type outfile: {None | str}
        @param unknowns_dest: optional destination path for unknown first names.
            Default: not collected
        @type unknowns_dest: {None | str}
        '''
        baby_nms_dict = self.import_baby_names(baby_names_file)
        instructor_names = self.import_instructor_names(instructor_names_file)
        try:
            if outfile is None:
                out_fd = sys.stdout
            else:
                out_fd = open(outfile, 'w')
            writer = csv.writer(out_fd)
            writer.writerow(['LastName', 'FirstName', 'MiddleName', 'Sex'])
            num_unknowns = 0
            if unknowns_dest is not None:
                unknowns = []
            
            for nm_obj in instructor_names.values():
                try:
                    sex = baby_nms_dict[nm_obj.first_nm]
                except KeyError:
                    # Unusual first name; not in dict
                    sex = 'U'
                    num_unknowns += 1
                    if unknowns_dest is not None:
                        unknowns.append(str(nm_obj))
                writer.writerow([nm_obj.last_nm,
                                 nm_obj.first_nm,
                                 nm_obj.mid_initial,
                                 sex
                                 ])
        finally:
            if outfile is None:
                out_fd.close()
            print(f"Wrote result to {outfile}")
            print(f"Number of unknowns: {num_unknowns}")
            if unknowns_dest is not None:
                try:
                    with open(unknowns_dest, 'w') as fd:
                        writer = csv.writer(fd)
                        for nm in unknowns:
                            writer.writerow([nm])
                except Exception as e:
                    print(f"Could not write unknowns file: {repr(e)}")
                else:
                    print(f"Wrote unknowns to {unknowns_dest}")

    #------------------------------------
    # import_instructor_names
    #-------------------
        
    def import_instructor_names(self, instructor_file):
        '''
        Read given file, which needs to be a single
        col names list as in __init__ header. Parses
        names, and returns list of InstructorName instances
        that hold first, last, and middle initial. 
        
        @param instructor_file: file with instructor names
        @type instructor_file: str
        @return: list of parsed instructor names
        @rtype: [InstructorName]
        '''
        
        nm_objs = {}
        with open(instructor_file, 'r') as fd:
            # Skip the header col, if there is one; but
            # the README.txt instructs MySQL export that
            # avoids a header:
            # next(fd)
            for line in fd:
                all_names = line.split(';')
                for nm in all_names:
                    # Parse the name:
                    nm_obj = InstructorName(nm)
                    # Don't save duplicates: just
                    # overwrite the name instance of 
                    # any previously found same same:
                    nm_objs[nm_obj._summary()] = nm_obj
        return nm_objs 

    #------------------------------------
    # import_baby_names 
    #-------------------
    
    def import_baby_names(self, baby_names_file):
        '''
        Expects historic baby names as follows:
        
			  name,gender,frequency
			  Mary,F,7065
			  Anna,F,2604
			  Emma,F,2003
			    ...

        Frequencies are ignored.

        @param baby_names_file: path to file of names
        @type baby_names_file: str
        @return: dict mapping first-name to {F|M}
        @rtype: {str : str}
        '''
        
        sex_dict = {}
        with open(baby_names_file, 'r', newline='') as fd:
            reader = csv.DictReader(fd)
            print(f"Importing baby names file {baby_names_file}...")
            for baby_name in reader:
                sex_dict[baby_name['name']] = baby_name['gender']
            print("Done importing baby names file")
        return sex_dict

# ---------------------- Class InstructorName -----------

class InstructorName:
    
    def __init__(self, nm_str):
        '''
        Given a name like one of these:
        
            Aalami, Oliver O
		    Aanjaneya, Mridul
		    Engler, Dawson, R   <------Sometimes three commas!
		    
		Parse, and create inst vars 'last_name', 'first_name',
		and 'middle_name'
		            
        @param nm_str: name
        @type nm_str: str
        '''
        # Get like ['Aalami', 'Oliver O'], 
        # or sometimes ['Engler', 'Dawson', 'R'] 
        nm_info = nm_str.strip().split(',')
        # Have the unusal 3-comma case?
        if len(nm_info) > 2:
            self.last_nm = nm_info[0].strip()
            self.first_nm = nm_info[1].strip()
            self.mid_initial = nm_info[2].strip()
            return
        
        last_nm = nm_info[0]
        try:
            # Split the 'Oliver O' in "Aalami, Oliver O": 
            first_nm, middle_initial = nm_info[1].strip().split(' ')
        except ValueError:
            # No middle initial:
            middle_initial = ''
            first_nm = nm_info[1]
            
        self.last_nm  = last_nm.strip()
        self.first_nm = first_nm.strip()
        self.mid_initial = middle_initial.strip() 

    #------------------------------------
    # _summary
    #-------------------
    
    def _summary(self):
        return f"{self.last_nm}_{self.first_nm}_{self.mid_initial}"

    #------------------------------------
    # __str__ 
    #-------------------

    def __str__(self):
        nm_str = f"{self.last_nm}, {self.first_nm}"
        if len(self.mid_initial) > 0:
            nm_str += f" {self.mid_initial}."
        return nm_str
    
    #------------------------------------
    # __eq__ 
    #-------------------
    
    def __eq__(self, other):
        return (
            other.last_nm == self.last_nm and \
            other.first_nm == self.first_nm and \
            other.mid_initial == self.mid_initial
            )


# ------------------------ Main ------------
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description="Guess sex by first names"
                                     )

    parser.add_argument('-o', '--outfile',
                        help='optional path to file for result; default: stdout.',
                        default=None)
    parser.add_argument('-u', '--unknowns',
                        help='optional path to where list of unknown entries are written; default: not collected')
    parser.add_argument('names_file',
                        type=str)
    parser.add_argument('baby_name_file',
                        type=str,
                        help='path to list of baby names with sex association')

    args = parser.parse_args()

    
    instructor_nms = '/Users/paepcke/Project/Carta/Data/Names/instructor_names_filtered.csv'
    baby_nms = '/Users/paepcke/Project/Carta/Data/Names/all_names.csv'
    guesser = NameSexGuesser(args.names_file,
                             args.baby_name_file,
                             outfile=args.outfile,
                             unknowns_dest=args.unknowns
                             )
