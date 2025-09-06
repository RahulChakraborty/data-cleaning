# data-cleaning
Data Cleaning Pipeline project with Open Refine, Pandas and YesWorkFlow Diagrams

Here is the simplest solution if you are getting unknown host error:

ssh-keygen -R <host>
For example,

ssh-keygen -R 192.168.3.10
# Setting up SSH Keys for Git Clone

Step 1: Check for existing SSH keys
$> ls -al ~/.ssh

Do you see any files named id_rsa and id_rsa.pub?

If yes go to Step 3

If no, you need to generate them

Step 2: Generate a new SSH key
$> ssh-keygen -t rsa -b 4096 -C "yourEmail"

Add your SSH key to the ssh-agent

$> eval "$(ssh-agent -s)"

$> ssh-add ~/.ssh/id_rsa

Step 3.1: Add the SSH key to your GIT account.
Get your public key

$> cat ~/.ssh/id_rsa.pub

Go to your GIT Account Settings (your profile picture in the upper right corner) -> Settings -> SSH and GPG 
keys -> New SSH key

Then paste the content of your public key into SSH keys

Step 3.2: Force SSH Client To Use Given Private Key
This is an alternative solution when you can't set keys on your Git account

$> sudo nano ~/.ssh/config

Host gitlab.domain.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_my_key
Step 4: Clone the project
$> git clone git@xxxxx.com:xxx/xxx/git
