# Large-Scale Web Tracking and Cookie Compliance: Evaluating One Million Websites under GDPR and ePrivacy with AI Categorization

This public repository contains the data, algorithms and code implementations that support the findings of the article *Large-Scale Web Tracking and Cookie Compliance: Evaluating One Million Websites under GDPR and ePrivacy with AI Categorization*.

## Software

Install python and the required packages listed in *requirements.txt* file. Also install the official *website-evidence-collector* from the EDPS official GitHub.

## Data files

Present in the "data" directory. It includes:

- **tranco.csv**: Full tranco list to perform the large-scale web tracking study (same version as the academic paper).
- **easyprivacy.txt**: publicly available filter list used by various ad-blocking and privacy-focused tools to block tracking scripts, tracking pixels, beacons, and other web elements that infringe on user privacy, used in the paper.
- **_bert_model_multi_final**: Directory where the pre-trained AI model is stored and ready to be used.
- **social_networks.txt**: Predefined set of regex rules to identify well-known social media URL patterns.
- **fingerprinting_domains.json**: File that contains well-known fingerprinting patterns.
- **wec-a.zip**: Binary files of the WEC software modified to accept cookie banners before the analyses (WEC-Accept).

## Massive Tracking Study (MTS)

To perform the MTS, enter on *mts* directory and execute the *massive_tracking_study.py* file, with the following parameters in order:

- **tranco_file.csv**: csv file with the Tranco list.
- **num_processes**: Number of parallel processes to spawn (recommended: number_of_cores x 1.5).

The script will save the results in two subdirectories, errors for errors and results for analyzed websites. The results are saved for each processed website in a file with name tranco_id.csv inside one of the subdirectories depending on the result. Result files are defined in the following format: 

- protocol, num_tracking_cookies, num_pixel_tracking, if_fingerprinting

Next, the script *merge_results_to_file.py* and *merge_errors_to_file.py* is used to merge all the MTS result data files into one single file: *merged_results.json*.

Finally, all the *process.py* and *plot.py* files can be executed to print numerical results and also the latex code to make result tables just as the paper. See each file for more precise documentation.

## Acceptance Tracking Study (ATS)

The same procedure as the MTS, but changing the WEC binary files by the WEC-A modified ones, available at the *data* folder.

## AI Categorizer

To categorize a sample of websites, enter on *ai-categorizer* directory and execute the *ai_categorizer.py* file, with the following parameters in order:

- **name_to_ai_sample_file.csv**: csv file in the Tranco list format to categorize, with an extra third integer column indicating wether the website provides HTTPS "1" or not "0" (extracted from the result of the *massive_tracking_study.py* and *prepare_ai.py*).
- **chromedriver_path**: Path to the chromedriver file (has to be consistent to the version of Google Chrome installed on the system).
- **num_processes**: Number of parallel processes to spawn (recommended: number_of_cores x 10).

The script will save the results in two subdirectories, errors_ai for errors and results_ai for categorized websites. The results of the categorization are saved for each processed website in a file with name tranco_id.csv inside one of the subdirectories depending on the result. Result files are defined in the following format: 

- cat1;cat2,[confidence_cat1,condidence_cat2].

The full list of categories are as follows: 

```
translation_dict = {
    'Empresa i Finances': 'Business and Finance',
    'Ciència, Tecnologia, Enginyeria i Matemàtiques': 'Science and Technology',
    'Videojocs': 'Video Games',
    'Ocupació': 'Employment',
    'Joc i Apostes': 'Gambling and Betting',
    'Literatura, Art i Cultura': 'Arts and Culture',
    'Compres': 'Shopping',
    'Religió i Espiritualitat': 'Religion and Spirituality',
    'Notícies': 'News',
    'Lleis, Govern i Política': 'Law and Politics',
    'Salut': 'Health',
    'Moda i Estil': 'Fashion',
    'Viatges i Turisme': 'Travel',
    'Jardineria i Plantes': 'Gardening',
    'Esport': 'Sports',
    'Menjar i Alimentació': 'Food and Nutrition',
    'Educació': 'Education',
    'Adults': 'Adults',
    'Animals i Mascotes': 'Animals and Pets',
    'Música': 'Music',
    'Habitatge': 'Housing',
    'Automoció': 'Automotive',
    'Xarxes Socials': 'Social Media',
    'NaN': 'NaN'
}
```

Next, the script *merge_ai_to_file.py* is used to merge all the AI result data files into one single file: *ai_res.json*.

Finally, *process_ai_results.py* can be executed to print numerical results of the categorized websites and also the latex code to make a table just as the paper. It needs the following parameters:

- **results_merged.json**: path of the file including the merged subdir results of the Massive Tracking Study (MTS).

It generates the following files:

- **img_categories.pdf**: bar chart of the category distribution, same format as the paper.
- **violation_table_cat.json**: data to build the violation table, same format as the paper, grouped by categories.


## Other

Folder with other python scripts that can be utilized, including:

- online and offline website check.
- *robots.txt* consideration.
- Result processing and plotting files from MTS and ATS.

## Results

This folder includes partial and final result files extracted from the execution of the algorithms and AI categorization for the Tranco list sample, illustrated in the paper.