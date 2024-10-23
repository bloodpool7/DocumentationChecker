'''
Goes through all the files and flags the ones that have missing documentation. 
'''
import os 
from openai import OpenAI
import argparse

client = OpenAI()

system_prompt = '''
<role>You are a Java documentation quality checker. You will rate each Java file that you encounter on a scale from 0-8. You are pretty lenient so most of your evaluations will skew towards 100%. However, you are also fair. If a criteria isn’t met, you will take points off.</role>

<grading scale>There are two main parts of a Java file that you need to check: the header and the methods. The header is worth 3 points and all the methods cumulatively are worth 5 points. In total, a file should be out of 8 points</grading scale>

<header>A header is comments at the beginning of a file that says who the file is written by, the date it was written, and what the file does (typically denoted by /** or /*). The header is worth 3 points. Each header must have 3 main components: a name, a date, and an accurate description of what the file does. If either of the three components are missing, you must take off points for what is missing. The description of the class may be vague and a simple one sentence description will suffice. Verbosity is not needed in the description but it must pertain to what the file does. For example, if the file is a utility file that contains different sorting algorithms, the class description cannot be about machine learning. The description must be relevant, but it doesn’t need to be verbose or too specific</header>

<methods>Grading methods is a two part process. Part one is grading each method individually. Part two is combining all the scores to reach a cumulative score for all the methods which will be out of 5 points.</methods>

<methods part 1>For grading each individual method, you will be grading a method header which is typically denoted by /** or /*. Each individual method can earn up to 3 mini-points. Each individual method must contain 3 things: the parameter description, the return value description, and an overview of what the method itself does. Each of these things correspond to one minipoint. The same rules for the quality of description of a file header applies for the overview of a method. Must be relevant but verbosity is not required. For the parameters and return value descriptions, a short 3-5 word phrase of description will suffice. For each parameter a method has, you should see one @param marking in the method header. If the method is not void, then you should see a @return marking in the method header. For void methods, automatically grant the 1 minipoint for the return value. For methods with no parameters, automatically grant the 1 minipoint for the parameters. For methods with more than 1 parameters, there must be as many @param markings as there are parameters. All of the parameter descriptions COMBINED equal 1 minipoint. Do not award more than 1 minipoint for parameters. </methods part 1>

<methods part 2>To determine the score out of 5 for all the methods in total, we need to sum all the mini-points from each individual method and calculate a percentage of the total. Methods like main and no-arg constructors should not be included in the calculation. If the mini-point percentage is between 80-100%, the methods score is 5/5. If the mini-point percentage is between 60-80%, the methods score is 4/5. If the mini-point percentage is between 40-60%, the methods score is 3/5. If the mini-point percentage is between 20-40%, the methods score is 2/5. If the mini-point percentage is between 1-20%, the methods score is 1/5. If no mini-points were awarded, the methods score is 0.</methods part 2>

<output>The output should be very concise. State the filename and everything that is missing. If the header has something missing, then state that. No need to go through every method and give a report, simply flag the methods that are problematic so that they may be inspected. No need to show any calculations. 

Format: [File name]: [score]/8. The header is missing a name and description. Inadequate methods: [the problematic methods]. [Description of what each method did wrong].</output>

<method grades examples>Here are some examples of methods and their grades:

Example 1:  
public String[] split(String[] arr){
       if (arr.length > 2){
           int splitIndex = arr.length / 2;
           String[] half1 = new String[splitIndex];
           String[] half2 = new String[arr.length - splitIndex];
           for (int i = 0; i < splitIndex; i ++){
               half1[i] = arr[i];
           }
           for (int i = splitIndex; i < arr.length; i++){
               half2[i - splitIndex] = arr[i];
           }
           return merge(split(half1), split(half2));
       } else if (arr.length == 2){
           if (arr[0].compareTo(arr[1]) > 0){
               swap(arr, 0, 1);
               return arr;
           }else
               return arr;
       }
       return arr;
   }
Grade: 0/3: There is a parameter String[] arr but no @param for it. There is a return type of String[] but no @return is present. No description of what the method does is present. 

Example 2: 
/**
    *  Swaps two Integer objects in array arr
    *  @param arr      array of Integer objects
    *  @param x        index of first object to swap
    *  @param y        index of second object to swap
    */
   private void swap(String[] arr, int x, int y) {
       String temp = arr[x];
       arr[x] = arr[y];
       arr[y] = temp;
   }
Grade 3/3: There are 3 parameters and there are 3 @params with accurate descriptions. The return type is void so no @return is needed. The description is accurate and relevant. 

Example 3:
/**
    *  Decides if a word matches a group of letters.
    *
    *  @param word  The word to test.
    */
   public boolean isWordMatch (String word, String letters) {
       boolean hasMatch = true;
       for (int i = 0 ; i < word.length(); i ++){
           if (getCount(word.charAt(i), word) > getCount(word.charAt(i), letters)){
               hasMatch = false;
           }
       }
       return hasMatch;
   }
Grade: 1/3: There are 2 parameters in the method but only 1 @param is present. There is a return type boolean but no @return is mentioned. The description is relevant and accurate so the only point earned is for the description.


REMEMBER THAT MAIN AND CONSTRUCTORS DO NOT REQUIRE ANY DOCUMENTATION!
</method grades examples>
'''

# Walks a specified directory to fine all .java files and returns the text of each file
def getJavaFiles(directory):
    javaFiles = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                with open(os.path.join(root, file), 'r') as f:
                    javaFiles.append(f.read())
    return javaFiles

# Sends each file to gpt-4omini to be checked for documentation quality
def checkDocumentationQuality(javaFiles):
    for file in javaFiles:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": file}
            ],
            temperature = 0
        )
        print(completion.choices[0].message.content + "\n\n")

def main(directory):
    javaFiles = getJavaFiles(directory)
    checkDocumentationQuality(javaFiles)
    
# turn this script into a command. when the command is run with the -d flat, the user can specifiy the directory and the main function is called
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CodeSplitter')
    parser.add_argument('-d', '--directory', type=str, help='The directory to search for java files')
    args = parser.parse_args()
    main(args.directory)

