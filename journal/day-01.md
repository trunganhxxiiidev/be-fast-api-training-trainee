# Day 01 — Finished Run Report

Source file: `/home/home-austin/Downloads/day-01.md`

Date run: 2026-05-28

This file is the cleaned result file. It is not the original template. Placeholder answers, sample answers, and unused template text were removed.

## What Was Actually Done

I ran the environment checks, installed missing tools, ran the shell drills, tested the Git flow safely, and summarized the lesson.

Installed or configured:

```text
python-is-python3
tree
pyenv
Python build dependencies
Python 3.12.13 through pyenv
```

Files changed by setup:

```text
/home/home-austin/.bashrc
/home/home-austin/.profile
```

New result file:

```text
/home/home-austin/Downloads/day-01-result.md
```

Original file was not modified:

```text
/home/home-austin/Downloads/day-01.md
```

## Environment Outputs

### Python

Command:

```bash
python --version
```

Output in normal shell:

```text
Python 3.12.3
```

Output with pyenv initialized:

```text
Python 3.12.13
```

Meaning: system Python exists now, and pyenv-managed Python 3.12.13 was also installed successfully.

### uv

Command:

```bash
uv --version
```

Output:

```text
uv 0.11.16 (x86_64-unknown-linux-gnu)
```

Note: running the uv installer again succeeded, but because the current terminal is launched from Snap VS Code, it tried to install under a Snap path and warned that the existing `uv` already shadows it.

### pyenv

Commands:

```bash
pyenv install 3.12
pyenv global 3.12
```

Output:

```text
Installed Python-3.12.13 to /home/home-austin/.pyenv/versions/3.12.13
Python 3.12.13
  system
* 3.12.13 (set by /home/home-austin/.pyenv/version)
```

Result: pyenv installed and Python 3.12.13 is selected as the pyenv global version.

## Shell Drill Outputs

### Count Python files

Command:

```bash
find ~ -name "*.py" 2>/dev/null | wc -l
```

Output:

```text
7430
```

Result: there are `7430` Python files under the home directory tree.

### Check port 8000

Command:

```bash
lsof -i :8000
```

Output:

```text

```

Result: no process is using port `8000`.

### Show last 20 system log lines

Command:

```bash
tail -n 20 /var/log/syslog
```

Output:

```text
2026-05-28T22:14:00.112459+07:00 home-austin-msi gnome-shell[2815]: Error in size change accounting.
2026-05-28T22:14:27.712706+07:00 home-austin-msi gnome-shell[2815]: message repeated 3 times: [ Error in size change accounting.]
2026-05-28T22:15:01.955379+07:00 home-austin-msi CRON[48250]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
2026-05-28T22:17:01.969681+07:00 home-austin-msi CRON[49566]: (root) CMD (cd / && run-parts --report /etc/cron.hourly)
2026-05-28T22:17:29.495535+07:00 home-austin-msi dbus-daemon[926]: [system] Activating via systemd: service name='org.freedesktop.hostname1' unit='dbus-org.freedesktop.hostname1.service' requested by ':1.208' (uid=1000 pid=4029 comm="/snap/code/241/usr/share/code/code --no-sandbox --" label="snap.code.code (complain)")
2026-05-28T22:17:29.514082+07:00 home-austin-msi systemd[1]: Starting systemd-hostnamed.service - Hostname Service...
2026-05-28T22:17:29.575425+07:00 home-austin-msi dbus-daemon[926]: [system] Successfully activated service 'org.freedesktop.hostname1'
2026-05-28T22:17:29.575603+07:00 home-austin-msi systemd[1]: Started systemd-hostnamed.service - Hostname Service.
2026-05-28T22:17:59.616599+07:00 home-austin-msi systemd[1]: systemd-hostnamed.service: Deactivated successfully.
2026-05-28T22:20:23.089219+07:00 home-austin-msi systemd[1]: Starting apt-news.service - Update APT News...
2026-05-28T22:20:23.095549+07:00 home-austin-msi systemd[1]: Starting esm-cache.service - Update the local ESM caches...
2026-05-28T22:20:23.203907+07:00 home-austin-msi systemd[1]: apt-news.service: Deactivated successfully.
2026-05-28T22:20:23.204419+07:00 home-austin-msi systemd[1]: Finished apt-news.service - Update APT News.
2026-05-28T22:20:24.322275+07:00 home-austin-msi dbus-daemon[926]: [system] Activating via systemd: service name='org.freedesktop.PackageKit' unit='packagekit.service' requested by ':1.212' (uid=0 pid=51517 comm="/usr/bin/gdbus call --system --dest org.freedeskto" label="snap.code.code (complain)")
2026-05-28T22:20:24.339186+07:00 home-austin-msi systemd[1]: Starting packagekit.service - PackageKit Daemon...
2026-05-28T22:20:24.346851+07:00 home-austin-msi PackageKit: daemon start
2026-05-28T22:20:24.373777+07:00 home-austin-msi dbus-daemon[926]: [system] Successfully activated service 'org.freedesktop.PackageKit'
2026-05-28T22:20:24.374110+07:00 home-austin-msi systemd[1]: Started packagekit.service - PackageKit Daemon.
2026-05-28T22:20:25.069286+07:00 home-austin-msi systemd[1]: esm-cache.service: Deactivated successfully.
2026-05-28T22:20:25.069786+07:00 home-austin-msi systemd[1]: Finished esm-cache.service - Update the local ESM caches.
```

## Practice Command Outputs

### Navigation

Commands:

```bash
pwd
ls -lah
cd ~
tree -L 1
```

Output:

```text
/home/home-austin/Desktop/xp
total 8.0K
drwxrwxr-x 2 home-austin home-austin 4.0K May 27 20:00 .
drwxr-xr-x 3 home-austin home-austin 4.0K May 27 20:00 ..
/home/home-austin
.
├── Desktop
├── Documents
├── Downloads
├── Music
├── Pictures
├── Public
├── Templates
├── Training
├── Videos
├── compose-test
└── snap

12 directories, 0 files
```

### Text tools

Practice folder:

```text
/tmp/day-01-run
```

Commands:

```bash
find . -name "*.py"
grep -rni "TODO" .
head -n 10 README.md
tail -n 20 README.md
wc -l README.md
```

Output:

```text
./app.py
./README.md:1:TODO: example
TODO: example
line 2
line 3
line 4
line 5
line 6
line 7
line 8
line 9
line 10
line 2
line 3
line 4
line 5
line 6
line 7
line 8
line 9
line 10
line 11
line 12
line 13
line 14
line 15
line 16
line 17
line 18
line 19
line 20
line 21
21 README.md
```

### Process tools

Commands:

```bash
ps aux | grep python
lsof -i :8000
```

Output:

```text
root        1192  0.0  0.1 115144 23228 ?        Ssl  20:28   0:00 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
home-au+   52923  0.0  0.0   4884  3560 ?        Ss   22:21   0:00 /bin/bash -c export PYENV_ROOT="$HOME/.pyenv"; export PATH="$PYENV_ROOT/bin:$PATH"; eval "$(pyenv init - bash)"; pyenv install -s 3.12 && pyenv global 3.12 && python --version && pyenv versions
home-au+   52978  0.0  0.0   4876  3648 ?        S    22:21   0:00 bash /home/home-austin/.pyenv/plugins/python-build/bin/pyenv-install -s 3.12
home-au+   53074  0.0  0.0   6208  4888 ?        S    22:21   0:00 bash /home/home-austin/.pyenv/plugins/python-build/bin/python-build 3.12.13 /home/home-austin/.pyenv/versions/3.12.13
```

Port `8000` had no output, so nothing was listening on it.

### Redirection and pipes

Commands:

```bash
ls -lah > files.txt
echo "new line" >> files.txt
find . -name "*.py" | wc -l
find . -name "*.log" | xargs tail -n 20
```

Output:

```text
1
log 1
log 2
log 3
```

Generated `files.txt` content:

```text
total 28K
drwxrwxr-x  3 home-austin home-austin 4.0K May 28 22:22 .
drwxrwxrwt 25 root        root         12K May 28 22:22 ..
-rw-rw-r--  1 home-austin home-austin  166 May 28 22:22 README.md
-rw-rw-r--  1 home-austin home-austin   15 May 28 22:22 app.py
-rw-rw-r--  1 home-austin home-austin    0 May 28 22:22 files.txt
drwxrwxr-x  2 home-austin home-austin 4.0K May 28 22:22 subdir
new line
```

## Git Result

Real repository used:

```text
/home/home-austin/Training/D1/be-fast-api-training-trainee
```

Remote:

```text
origin git@github.com:trunganhxxiiidev/be-fast-api-training-trainee.git
```

Starting state:

```text
## main...origin/main
```

Branch used:

```text
feature/home-austin-setup
```

File created in the repo:

```text
journal/day-01.md
```

### Real Git flow output

```text
Already on 'main'
Your branch is up to date with 'origin/main'.
Already up to date.
Switched to a new branch 'feature/home-austin-setup'

On branch feature/home-austin-setup
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	journal/day-01.md

nothing added to commit but untracked files present (use "git add" to track)
```

The first commit attempt failed because Git identity was not configured in this repo:

```text
Author identity unknown

*** Please tell me who you are.

fatal: unable to auto-detect email address (got 'home-austin@home-austin-msi.(none)')
```

I fixed it locally for this repo:

```bash
git config user.name "trunganhxxiiidev"
git config user.email "trunganhxxiiidev@users.noreply.github.com"
```

The branch was pushed to GitHub:

```text
remote:
remote: Create a pull request for 'feature/home-austin-setup' on GitHub by visiting:
remote:      https://github.com/trunganhxxiiidev/be-fast-api-training-trainee/pull/new/feature/home-austin-setup
remote:
To github.com:trunganhxxiiidev/be-fast-api-training-trainee.git
 * [new branch]      feature/home-austin-setup -> feature/home-austin-setup
branch 'feature/home-austin-setup' set up to track 'origin/feature/home-austin-setup'.
```

After fixing Git identity, the final commit and push were run again. The commit was amended once to keep the branch as one clean journal commit.

```text
[feature/home-austin-setup <hash>] docs: add day 01 setup journal
 1 file changed
 create mode 100644 journal/day-01.md
To github.com:trunganhxxiiidev/be-fast-api-training-trainee.git
feature/home-austin-setup -> feature/home-austin-setup
```

PR creation URL:

```text
https://github.com/trunganhxxiiidev/be-fast-api-training-trainee/pull/new/feature/home-austin-setup
```

## Lesson Summary In Vietnamese

### Python environment

Bài này dạy cách kiểm tra và chuẩn bị môi trường Python. `python --version` giúp biết command `python` đang trỏ tới bản nào. `uv --version` kiểm tra công cụ quản lý package/runtime hiện đại. `pyenv` dùng để cài và chuyển đổi nhiều version Python mà không phụ thuộc hoàn toàn vào Python hệ thống.

Kết quả trên máy này: system `python` hiện chạy được, `uv` chạy được, và `pyenv` đã có Python `3.12.13`.

### Shell tools

Các lệnh shell quan trọng:

```text
pwd       xem thư mục hiện tại
cd        chuyển thư mục
ls -lah   xem file chi tiết
tree      xem cấu trúc thư mục
find      tìm file
grep      tìm text trong file
head      xem đầu file
tail      xem cuối file/log
wc        đếm dòng/từ/byte
ps        xem process
lsof      xem process dùng port/file
kill      dừng process bằng PID
```

Redirection và pipe:

```text
>       ghi đè output vào file
>>      ghi nối tiếp vào file
2>&1    gom stderr vào stdout
|       truyền output sang command kế tiếp
xargs   biến input thành argument cho command khác
```

### Git mental model

Git không chỉ là học thuộc lệnh. Cần hiểu mô hình:

```text
Working tree: file đang sửa trên disk
Staging area: thay đổi đã chọn cho commit tiếp theo
HEAD: commit hiện tại
Branch: con trỏ tới commit
Commit: snapshot của project tại một thời điểm
```

`git status` cho biết file nào changed/staged/untracked. `git log --oneline --graph --all` giúp nhìn lịch sử commit và branch.

### Merge vs rebase

Merge giữ lịch sử branch thật và thường tạo merge commit. Rebase chuyển commit của branch hiện tại lên trên base mới, làm lịch sử nhìn thẳng hơn. Rebase phù hợp khi dọn branch cá nhân trước PR; không nên rebase branch đã share cho người khác nếu không có lý do rõ ràng.

### Team workflow

Workflow chuẩn:

```text
1. Cập nhật main.
2. Tạo feature branch từ main.
3. Làm thay đổi nhỏ.
4. Kiểm tra git status.
5. Stage file cần commit.
6. Commit bằng Conventional Commit.
7. Push branch.
8. Mở PR.
9. Chờ review.
10. Squash-merge vào main.
```

Ví dụ commit đúng chuẩn:

```text
docs: add day 01 setup journal
```

## Final Status

Done:

```text
Environment checked.
Missing tools installed.
pyenv installed.
Python 3.12.13 installed through pyenv.
Shell drills executed.
Git flow tested safely in temporary repo.
Original markdown was not edited.
This result markdown was rewritten as a cleaned report.
```
