# Gather
Gather data of water levels in main reservoirs in Kerala


1. Get the last commit SHA of a specific branch
# GET /repos/:owner/:repo/branches/:branch_name
last_commit_sha = response.json()['commit']['sha']

2. Create the blobs with the file's content (encoding base64 or utf-8)

# POST /repos/:owner/:repo/git/blobs
# {
#  "content": "hello world",
#  "encoding": "utf-8"
# }
utf8_blob_sha = response.json()['sha']

3. Create a tree which defines the folder structure

# POST repos/:owner/:repo/git/trees/
# {
#   "base_tree": last_commit_sha,
#   "tree": [
#     {
#       "path": "myfolder/base64file.txt",
#       "mode": "100644",
#       "type": "blob",
#       "sha": base64_blob_sha
#     }
#   ]
# }
tree_sha = response.json()['sha']

4. Create the commit
# POST /repos/:owner/:repo/git/commits
# {
#   "message": "Add new files at once programatically",
#   "author": {
#     "name": "Jan-Michael Vincent",
#     "email": "JanQuadrantVincent16@rickandmorty.com"
#   },
#   "parents": [
#     last_commit_sha
#   ],
#   "tree": tree_sha
# }
new_commit_sha = response.json()['sha']

5. Update the reference of your branch to point to the new commit SHA (on master branch example)

# PATCH /repos/:owner/:repo/git/refs/heads/:branch
# {
#     "sha": new_commit_sha
# }