Copyright (c) 2015 Crowd Dynamics Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


from flickr_wrapper import search_photos, get_info, get_related_tags, is_food, get_image
from overlay_whole import draw_text,text_size,overlay_whole_begin
import webbrowser
import random
import re
import json
import urllib
import os

# list of noun and modifier words to find images
def find_images(nouns, modifiers=None):
    print("find images called, nouns: " + str(nouns) + ", modifiers: " + str(modifiers))

    photos = search_photos(nouns)
    print("number of photos found: " + str(len(photos)))
    if photos:
        print("retrieving metadata for each image...")
        urls_and_tags = []
        for photo in photos:
            photo_id = photo['id']
            try:
                photo_info = get_info(photo_id)
            except:
                continue
            data = {}
            data['url'] = photo_info['url']
            data['tags'] = photo_info['tags']
            data['user_id'] = photo_info['user_id']
            data['photo_id'] = photo_id
            urls_and_tags.append(data)

        return urls_and_tags
    else:
        return 0


def is_int(num):
    try: 
        int(s)
        return True
    except ValueError:
        return False  

def ignore(tag):
    """
    given a tag as a string
    returns True or False whether to ignore this tag

    """
    # if it contains digits, ignore
    _digits = re.compile('\d')
    if bool(_digits.search(tag)):
        return True

    ignore_list = ['canon', 'camera', 'closeup', 'pics', 'photo', 'image']

    tag = tag.lower()   # to lower case

    # check whether it is camera focal length
    is_camera = False
    
    temp = tag.replace(' ', '')

    if tag[-2:] == "mm":    # if last 2 characters are mm
        temp = temp[:-2]     # remove the last 2 characters
        is_camera = is_int(temp)

    if is_camera:
        return True
    else:
        if tag in ignore_list:
            return True
        else:
            return False

def relevance_score(originalTags, tags):
    """
    originalTag is a single string
    and tags are the list of tags to check for
    relevant with respect to the originalTag

    """
    return len(originalTags)/float(len(tags))

    # relevance = 0

    # for tag in tags:
    #     if not ignore(tag): # if tag should not be ignored
    #         try:
    #             related_tags = get_related_tags(tag)
    #         except Exception as e:
    #             print("exception processing tag: " + tag)
    #             continue    # go to next iteration of loop

    #         # for each original tag
    #         # if an original tag is part of the related tags of the current tag
    #         # increment score by 1
    #         for originalTag in originalTags:
    #             if originalTag in related_tags:
    #                 relevance += 1
    #                 break
    #             else:
    #                 found = False
    #                 for related_tag in related_tags:
    #                     if originalTag in related_tag:  # check substring
    #                         relevance += 1
    #                         found = True
    #                         break
    #                 if found:
    #                     break

    # return float(relevance)/len(tags)

# given the query terms and a list of images
# returns a dictionary with key: tags and value: co-occurence count
def find_weight(query, images):
    d = {}

    for image in images:
        tags = image['tags']
        for tag in tags:
            if tag not in d:
                related = get_related_tags(tag)
                
                if related is not None:
                    intersection_size = len(list(set(query) & set(related)))
                    
                    d[tag] = intersection_size

                    print("word " + tag + ", intersect size " + str(intersection_size))

    return d

def begin(nouns,msg,file_name):
    # load from file
    #tags_data = json.load(open("data.txt"))
        tags_data = {}	
    #while(1):
        #i = raw_input("Please enter a comma delimited list of tags\n")
		
        #i = i.replace(' ', '')
        #nouns = i.split(',')

        print("input list: ", nouns)
        img_list = find_images(nouns+['food'])
        if img_list == 0:
            return 0
        results = []

        d={}

        # calculate score of each image
        # for each tag of the image, if the related tags of the tag has all the nouns
        # increase the score by 1
        for img in img_list:
            tags = img['tags']
            tags = list(set(tags) - set(nouns))

            score = 0

            for tag in tags:
                # if we have not seen this tag before
                if tag not in tags_data:
                    related = get_related_tags(tag)
                    print type(tag)
                    if related is not None:
                        tags_data[tag] = related    # update data

                        intersection_size = len(list(set(nouns) & set(related)))
                        
                        d[tag] = intersection_size
                        
                        print("word " + tag + ", intersect size " + str(intersection_size))
                        
                        if d[tag] == len(nouns):
                            score += 1
                # tag has been seen before
                else:
                    print("tag seen before")

                    if tag not in d:
                        intersection_size = len(list(set(nouns) & set(tags_data[tag])))
                        d[tag] = intersection_size    
                        print("word " + tag + ", intersect size " + str(intersection_size))

                    if d[tag] == len(nouns):
                        score += 1

            results.append({'object': img, 'score': score})

        # save to file
        json.dump(tags_data, open("data.txt",'w'))


        print("scoring complete...")
        sorted_results = sorted(results, key=lambda k: k['score'], reverse=True) 
        print(sorted_results)

        #for result in sorted_results:
         #   _input = raw_input("Press enter for next image, q for next input list")
         #   if _input == "q":
         #       break
        check = 1
        count = 0
        for result in sorted_results:          
         while(check == 1 and count < 10):
            print("score: " + str(result['score']))

            photo_id = result["object"]["photo_id"]
            image_src_url = get_image(photo_id)

            if image_src_url:

                print("image source url ", image_src_url)
    	    	# save image
    	        urllib.urlretrieve(image_src_url, "/Local/Users/dev/NetworkLabs/working/img.jpg") 
	
    	    	# run overlay script
    	    	#os.system("python /home/dev/NetworkLabs/working/overlay_whole.py")
                overlay_whole_begin(msg,file_name)
    	        check = 0	
    	    	# webbrowser.open(result['object']['url'])
            else:
                print("In else")
                check = 1
                print("image does not allow download")
                count = count+1
            print("")
         if check==0:
             return 1
         else:
             return 0

def begin_localimg(msg,file_name):
	overlay_whole_begin(msg,file_name)

 
if __name__=="__main__":
   # begin()
	begin_localimg()



# for 50 images come up with all the unique words that appear across all these images
# for each of the tags, find the top related tags and if both original words appear, assign weight 2 to the word, if only 1 appear assign weight 1
# sum up all the tags for each image and that will be the score


# search for images with nouns plus food
# count all tags for each image that fully match the nouns (excluding food)
