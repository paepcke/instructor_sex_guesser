# name_sex_guesser
Combines a list of English first names with a list of last/first[/middle-initial] entries. Outputs a .csv last,first,middle-initial,<sex> where sex in {M,F,U}. A 'U' stands for unknown, and occurs when the given baby list does not have an entry for the first name.

Optionally, creates an additional file with a list of the unknown entries.

Baby names with their sex are taken from the [Social Security Administration] (https://www.ssa.gov/oact/babynames/names.zip). The file is not included here. To create after downloading into an otherwise empty directory:

'''
unzip names.zip
cat *.txt > all_names.csv
'''

Starting point is a file with entries such as:

		   Abbas, Jennifer L
		   Abbas, Jennifer L
		   Abbas, Jennifer L; Fu, Fei-Fei
		   Aalamo, Oliver O
		   Aalamo, Oliver O; Yock, Paul R
		   Aanjaneya, Mridul

Note: OK to have duplicates; they will be removed. OK to have semicolon separated lists of names in one row Middle initials may or may not be present.

Usage (specific to one particular db, but generalizable):

```
mysql -u <my_name> -p  --skip-column-names --silent carta -e "select distinct instructors from all_eval_instructors" > /tmp/names_to_resolve.csv

name_sex_guesser.py --outfile /tmp/sexed_names.csv \
                    --unknowns /tmp/unknowns.csv \
                    /tmp/names_to_resolve \
                    /tmp/baby_names
```