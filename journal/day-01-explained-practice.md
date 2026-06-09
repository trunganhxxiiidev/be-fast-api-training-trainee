# Day 01 — Giai Thich Chi Tiet Va Bai Tap Thuc Hanh

Nguon da doc: `/home/home-austin/Downloads/day-01-result.md`

File nay dung de hoc lai bai lab Day 01 bang tieng Viet. File nay khong phai output report, ma la ban giai thich chi tiet: lenh do de lam gi, thuat ngu nghia la gi, vi sao can config shell, va co cac command block san de copy thuc hanh.

Khong push Git tu file nay.

## 0. Ban Can Hieu Gi Sau Bai Nay

Sau bai Day 01, muc tieu la nam duoc 4 nhom kien thuc:

1. Moi truong Python: `python`, `pyenv`, `uv`, PATH, shell config.
2. Lenh Linux/Shell: di chuyen thu muc, tim file, doc log, tim process, pipe, redirect.
3. Git workflow: branch, commit, remote, push, PR.
4. Cach doc output terminal: thay output rong, error, warning, status va hieu y nghia.

Tu duy quan trong: dung chi hoc thuoc lenh. Can hieu lenh do hoi he thong cai gi, sua cai gi, doc file nao, hay day du lieu di dau.

## 1. Tong Quan Cac File Trong Lab

Trong result co nhac cac file nay:

```text
/home/home-austin/Downloads/day-01.md
/home/home-austin/Downloads/day-01-result.md
/home/home-austin/.bashrc
/home/home-austin/.profile
/home/home-austin/Training/D1/be-fast-api-training-trainee/journal/day-01.md
```

Giai thich:

| File | Y nghia |
|---|---|
| `day-01.md` | File bai tap goc, co placeholder de dien output |
| `day-01-result.md` | File ket qua da chay lenh va tong hop |
| `.bashrc` | File cau hinh chay moi lan mo interactive Bash shell |
| `.profile` | File cau hinh cho login shell, thuong dung de set PATH moi truong |
| `journal/day-01.md` | File journal duoc tao trong repo training de commit/push |

Luu y ve dau `~`:

```text
~ = home directory cua user hien tai
```

Voi user hien tai:

```text
~ = /home/home-austin
```

Vi du:

```text
~/.bashrc = /home/home-austin/.bashrc
~/.profile = /home/home-austin/.profile
```

Ban ghi `.~ /bashzc` hoac `bashzc` co the la go nham. Ten dung trong Bash la:

```text
~/.bashrc
```

## 2. Shell La Gi?

Shell la chuong trinh nhan lenh tu ban, doc lenh, roi yeu cau Linux chay lenh do.

Vi du ban go:

```bash
ls -lah
```

Shell se:

1. Doc chuoi `ls -lah`.
2. Tim chuong trinh `ls` trong PATH.
3. Chay `ls` voi options `-lah`.
4. In output ra terminal.

Mot so shell pho bien:

| Shell | Mo ta |
|---|---|
| `bash` | Mac dinh pho bien tren Linux |
| `zsh` | Pho bien cho dev, hay dung voi oh-my-zsh |
| `fish` | Than thien, autosuggestion manh |
| `sh` | Shell POSIX toi thieu, hay dung trong script portable |

Kiem tra shell hien tai:

```bash
echo "$SHELL"
ps -p $$ -o comm=
```

Kiem tra cac shell co tren may:

```bash
cat /etc/shells
```

## 3. `.bashrc`, `.profile`, `.zshrc` La Gi?

Day la cac file cau hinh shell. Chung quy dinh PATH, alias, prompt, plugin, va init tools nhu `pyenv`.

### 3.1 `.bashrc`

Duong dan:

```text
~/.bashrc
```

Dung cho interactive non-login Bash shell. Noi don gian: khi ban mo terminal moi bang Bash, `.bashrc` thuong se duoc doc.

Trong lab, file nay duoc them:

```bash
export PYENV_ROOT="$HOME/.pyenv"
case ":$PATH:" in
  *":$PYENV_ROOT/bin:"*) ;;
  *) export PATH="$PYENV_ROOT/bin:$PATH" ;;
esac
eval "$(pyenv init - bash)"
```

Giai thich tung dong:

```bash
export PYENV_ROOT="$HOME/.pyenv"
```

Khai bao bien moi truong `PYENV_ROOT`, noi pyenv duoc cai. Tren may nay la:

```text
/home/home-austin/.pyenv
```

```bash
case ":$PATH:" in
  *":$PYENV_ROOT/bin:"*) ;;
  *) export PATH="$PYENV_ROOT/bin:$PATH" ;;
esac
```

Doan nay them `~/.pyenv/bin` vao dau PATH neu chua co. Them vao dau PATH nghia la shell se uu tien tim `pyenv` o do truoc.

```bash
eval "$(pyenv init - bash)"
```

Lenh nay nap shell integration cua pyenv. No giup `python`, `pip`, va cac shim cua pyenv hoat dong dung theo version dang chon.

### 3.2 `.profile`

Duong dan:

```text
~/.profile
```

Thuong duoc doc khi login shell bat dau. File nay hop de set bien moi truong co ban nhu PATH.

Trong lab, `.profile` duoc them doan:

```bash
export PYENV_ROOT="$HOME/.pyenv"
case ":$PATH:" in
  *":$PYENV_ROOT/bin:"*) ;;
  *) export PATH="$PYENV_ROOT/bin:$PATH" ;;
esac
```

No giup login shell biet pyenv nam o dau.

### 3.3 `.zshrc`

Neu dung Zsh, file cau hinh tuong duong la:

```text
~/.zshrc
```

Neu dung `zsh + pyenv`, thuong can them:

```zsh
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
```

### 3.4 Fish config

Neu dung Fish shell:

```text
~/.config/fish/config.fish
```

Pyenv cho Fish thuong se khac syntax Bash/Zsh:

```fish
set -Ux PYENV_ROOT $HOME/.pyenv
fish_add_path $PYENV_ROOT/bin
pyenv init - fish | source
```

## 4. PATH La Gi?

`PATH` la danh sach cac thu muc shell se tim executable.

Xem PATH:

```bash
echo "$PATH"
```

In moi folder tren mot dong:

```bash
echo "$PATH" | tr ':' '\n'
```

Vi du ban go:

```bash
python --version
```

Shell se tim file executable ten `python` trong tung folder cua PATH. Folder nao nam truoc thi uu tien truoc.

Tim command dang duoc shell dung:

```bash
command -v python
command -v pyenv
command -v uv
command -v git
```

Xem tat ca version command cung ten:

```bash
type -a python
type -a uv
```

## 5. Python He Thong, pyenv Python, uv Khac Nhau The Nao?

### 5.1 Python he thong

Python he thong la Python cai bang package manager cua OS, vi du APT tren Ubuntu.

Trong result:

```text
Python 3.12.3
```

Day la Python he thong sau khi cai `python-is-python3`.

Kiem tra:

```bash
python --version
python3 --version
command -v python
command -v python3
```

### 5.2 `python-is-python3` la gi?

Tren Ubuntu, doi khi chi co command `python3`, khong co `python`.

Package `python-is-python3` tao lien ket de:

```text
python -> python3
```

Vi vay sau khi cai package nay, lenh sau moi chay duoc:

```bash
python --version
```

### 5.3 pyenv la gi?

`pyenv` la tool quan ly nhieu version Python trong home directory cua user.

No cho phep:

```bash
pyenv install 3.12
pyenv global 3.12
pyenv local 3.12
pyenv versions
```

Dung khi:

1. Project A can Python 3.10.
2. Project B can Python 3.12.
3. He thong Ubuntu co Python rieng, khong nen pha.

Pyenv cai Python vao:

```text
~/.pyenv/versions/
```

Trong result:

```text
/home/home-austin/.pyenv/versions/3.12.13
```

### 5.4 pyenv hoat dong nhu the nao?

Pyenv dung co che `shims`.

Khai niem:

```text
Shim = file trung gian dung de chon version Python dung truoc khi chay Python that
```

Luong chay don gian:

```text
Ban go: python
Shell tim trong PATH
PATH gap ~/.pyenv/shims/python
Shim hoi pyenv: project nay dung Python nao?
Pyenv chon version
Shim chay Python that trong ~/.pyenv/versions/...
```

Thu tu uu tien version pyenv:

1. Bien moi truong `PYENV_VERSION`.
2. File `.python-version` trong project hien tai.
3. File global `~/.pyenv/version`.
4. System Python.

Kiem tra:

```bash
pyenv version
pyenv versions
pyenv which python
python --version
```

Dung `pyenv local` trong mot project:

```bash
cd /path/to/project
pyenv local 3.12.13
cat .python-version
python --version
```

Lenh nay tao file:

```text
.python-version
```

File do bao cho pyenv: folder/project nay dung Python version nao.

### 5.5 uv la gi?

`uv` la tool Python hien dai cua Astral. No co the thay the nhieu cong cu cu:

| Tool cu | uv co the lam |
|---|---|
| `pip` | Cai package |
| `venv` | Tao virtual environment |
| `pip-tools` | Lock dependencies |
| `pyenv` mot phan | Cai/chay Python version trong mot so workflow |
| `poetry` mot phan | Quan ly project Python |

Trong lab chi kiem tra:

```bash
uv --version
```

Nhung khi lam project that, hay dung:

```bash
uv init
uv venv
uv pip install fastapi
uv pip freeze
uv run python --version
```

### 5.6 uv hoat dong nhu the nao?

`uv` la executable doc lap, viet bang Rust, chay nhanh. Khi ban dung `uv pip install`, no giai dependency, tai package, va cai vao virtual environment hien tai.

Workflow don gian:

```bash
mkdir -p ~/Training/uv-demo
cd ~/Training/uv-demo
uv venv
source .venv/bin/activate
uv pip install requests
python -c "import requests; print(requests.__version__)"
```

Giai thich:

| Lenh | Lam gi |
|---|---|
| `uv venv` | Tao `.venv` |
| `source .venv/bin/activate` | Kich hoat virtual env |
| `uv pip install requests` | Cai package vao env |
| `python -c ...` | Chay mot dong Python de test |

### 5.7 Virtual environment la gi?

Virtual environment la moi truong Python rieng cho tung project. No tranh cai package lung tung vao Python he thong.

Thu muc thuong gap:

```text
.venv/
```

Khi activate:

```bash
source .venv/bin/activate
```

Prompt co the hien:

```text
(.venv)
```

Thoat env:

```bash
deactivate
```

## 6. Snap VS Code Va Shadow Command

Trong result co note:

```text
current terminal is launched from Snap VS Code
it tried to install under a Snap path
existing uv already shadows it
```

Giai thich:

Ban dang dung VS Code ban Snap. Snap co moi truong rieng, nen mot so bien moi truong bi doi:

```text
SNAP=/snap/code/241
GTK_PATH=/snap/code/241/...
```

Khi chay installer trong terminal cua Snap VS Code, tool co the nghi home/path la path ben trong Snap, dan toi cai vao vi tri la:

```text
/home/home-austin/snap/code/241/.local/bin
```

`shadowed` nghia la co 2 command ten giong nhau, nhung command nam truoc trong PATH se duoc dung.

Kiem tra:

```bash
type -a uv
echo "$PATH" | tr ':' '\n'
```

Neu thay nhieu `uv`, command dau tien la command shell se dung.

## 7. APT Va Build Dependencies

### 7.1 APT la gi?

APT la package manager cua Ubuntu/Debian.

Lenh thuong dung:

```bash
sudo apt update
sudo apt install tree
sudo apt remove tree
apt-cache policy tree
dpkg -s tree
```

Giai thich:

| Lenh | Lam gi |
|---|---|
| `apt update` | Cap nhat danh sach package |
| `apt install` | Cai package |
| `apt remove` | Go package |
| `apt-cache policy` | Xem version/candidate/repo |
| `dpkg -s` | Xem package da cai |

Trong lab da cai:

```text
python-is-python3
tree
build-essential
libssl-dev
zlib1g-dev
libbz2-dev
libreadline-dev
libsqlite3-dev
libffi-dev
liblzma-dev
...
```

### 7.2 Build dependencies la gi?

Pyenv build Python tu source. Muon build Python can compiler va thu vien he thong.

Vi du:

| Dependency | Dung de |
|---|---|
| `build-essential` | Compiler `gcc`, `make` |
| `libssl-dev` | Ho tro SSL/TLS cho Python |
| `zlib1g-dev` | Nen/giai nen zlib |
| `libreadline-dev` | Ho tro shell input tot hon |
| `libsqlite3-dev` | Module sqlite trong Python |
| `libffi-dev` | Foreign function interface |
| `liblzma-dev` | Ho tro xz/lzma compression |

Neu thieu dependency, Python van co the build fail hoac build xong nhung thieu module.

## 8. Giai Thich Cac Lenh Shell Trong Lab

### 8.1 `pwd`

```bash
pwd
```

In ra current working directory.

Vi du:

```text
/home/home-austin/Desktop/xp
```

Dung khi ban muon biet minh dang o dau truoc khi chay lenh nguy hiem.

### 8.2 `ls -lah`

```bash
ls -lah
```

Giai thich options:

| Option | Nghia |
|---|---|
| `-l` | Long format, hien permission, owner, size, time |
| `-a` | Hien ca hidden files bat dau bang `.` |
| `-h` | Human readable size, vi du `4.0K`, `10M` |

Thu:

```bash
ls
ls -l
ls -la
ls -lah
```

### 8.3 `cd`

```bash
cd ~
cd /tmp
cd -
cd ..
```

Giai thich:

| Lenh | Lam gi |
|---|---|
| `cd ~` | Ve home |
| `cd /tmp` | Chuyen den `/tmp` |
| `cd -` | Quay lai thu muc truoc do |
| `cd ..` | Len thu muc cha |

### 8.4 `tree`

```bash
tree -L 1
```

In cau truc thu muc dang cay.

`-L 1` nghia la chi hien 1 cap. Neu khong gioi han, thu muc lon se in rat nhieu.

Thu:

```bash
tree -L 1 ~
tree -L 2 ~/Training
```

### 8.5 `find`

Trong result:

```bash
find ~ -name "*.py" 2>/dev/null | wc -l
```

Giai thich:

| Phan | Nghia |
|---|---|
| `find ~` | Tim bat dau tu home directory |
| `-name "*.py"` | Chi lay file/folder co ten ket thuc `.py` |
| `2>/dev/null` | Bo qua loi permission/error |
| `| wc -l` | Dem so dong output |

Lenh find can hoc:

```bash
find . -name "*.py"
find . -type f -name "*.md"
find . -type d -name ".git"
find . -type f -size +10M
find . -type f -mtime -1
find . -type f -name "*.log" -delete
```

Can than voi:

```bash
find . -delete
```

Lenh nay xoa file. Chi dung khi chac chan.

### 8.6 `grep`

Trong result:

```bash
grep -rni "TODO" .
```

Giai thich:

| Option | Nghia |
|---|---|
| `-r` | Recursive, tim trong thu muc con |
| `-n` | Hien line number |
| `-i` | Ignore case, khong phan biet hoa thuong |

Vi du:

```bash
grep "TODO" README.md
grep -n "TODO" README.md
grep -r "TODO" .
grep -rni "todo" .
grep -rni --exclude-dir=.git "password" .
```

Dung `grep` de tim nhanh text trong project.

### 8.7 `head`

```bash
head -n 10 README.md
```

In 10 dong dau file.

Thu:

```bash
head README.md
head -n 5 README.md
```

### 8.8 `tail`

```bash
tail -n 20 /var/log/syslog
```

In 20 dong cuoi file.

Hay dung de doc log vi log moi thuong nam cuoi file.

Lenh hay dung:

```bash
tail -n 50 app.log
tail -f app.log
tail -n 100 -f app.log
```

`tail -f` nghia la follow file, log moi ghi vao se hien tiep.

### 8.9 `wc`

```bash
wc -l README.md
```

Dem line.

Options:

| Option | Nghia |
|---|---|
| `-l` | So dong |
| `-w` | So tu |
| `-c` | So byte |

Vi du:

```bash
wc -l README.md
wc -w README.md
find . -name "*.py" | wc -l
```

### 8.10 `ps`

```bash
ps aux | grep python
```

`ps` hien process dang chay.

Giai thich `aux`:

| Phan | Nghia gan dung |
|---|---|
| `a` | Hien process cua moi user |
| `u` | Hien user/CPU/memory |
| `x` | Hien ca process khong gan terminal |

Thu:

```bash
ps aux | head
ps aux | grep python
ps aux | grep uvicorn
```

### 8.11 `lsof`

```bash
lsof -i :8000
```

`lsof` = list open files. Tren Linux, socket/port cung duoc xem nhu file resource.

Lenh tren hoi: co process nao dang dung port `8000` khong?

Neu co output, thuong se thay:

```text
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python  12345 user   ...  TCP *:8000 (LISTEN)
```

Can stop process:

```bash
kill 12345
```

Neu khong stop:

```bash
kill -9 12345
```

Chi dung `kill -9` khi can, vi no ep process chet ngay, khong cho cleanup.

### 8.12 `kill`

```bash
kill <PID>
```

Gui tin hieu yeu cau process dung lai.

Thuong dung:

```bash
kill 12345
kill -TERM 12345
kill -9 12345
```

### 8.13 `journalctl`

Neu khong co `/var/log/syslog`, co the dung:

```bash
journalctl -n 20 --no-pager
```

`journalctl` doc log cua systemd.

Lenh hay dung:

```bash
journalctl -n 50 --no-pager
journalctl -f
journalctl -u docker --no-pager
```

## 9. Redirection Va Pipe

### 9.1 `>`

```bash
ls -lah > files.txt
```

Ghi output vao `files.txt`. Neu file da co noi dung, no bi ghi de.

### 9.2 `>>`

```bash
echo "new line" >> files.txt
```

Ghi them vao cuoi file, khong xoa noi dung cu.

### 9.3 `|`

```bash
find . -name "*.py" | wc -l
```

Pipe lay output cua command ben trai dua vao input cua command ben phai.

Doc la:

```text
Tim file .py, roi dem so dong ket qua
```

### 9.4 `2>/dev/null`

```bash
find ~ -name "*.py" 2>/dev/null
```

`2` la stderr. `/dev/null` la noi bo rac. Lenh nay bo qua error output.

Su dung khi tim trong home ma gap folder khong co permission.

### 9.5 `2>&1`

```bash
some-command > output.log 2>&1
```

Gom stdout va stderr cung vao `output.log`.

### 9.6 `xargs`

```bash
find . -name "*.log" | xargs tail -n 20
```

`find` in danh sach file. `xargs` bien danh sach do thanh argument cho `tail`.

Can an toan voi ten file co space:

```bash
find . -name "*.log" -print0 | xargs -0 tail -n 20
```

## 10. Git: Giai Thich Toan Bo Thuat Ngu Trong Result

### 10.1 Repository

Repo la project duoc Git quan ly. Thu muc repo co folder:

```text
.git/
```

Kiem tra co phai repo khong:

```bash
git status
```

Neu khong phai repo:

```text
fatal: not a git repository
```

### 10.2 Working tree

Working tree la file tren disk ma ban dang sua.

Vi du ban sua:

```text
journal/day-01.md
```

Thi file do nam trong working tree.

### 10.3 Staging area / index

Staging area la noi chuan bi file cho commit tiep theo.

Them file vao staging:

```bash
git add journal/day-01.md
```

### 10.4 Commit

Commit la snapshot cua project tai mot thoi diem.

Tao commit:

```bash
git commit -m "docs: add day 01 setup journal"
```

Commit message gom:

```text
docs: add day 01 setup journal
```

`docs` la type theo Conventional Commits, nghia la thay doi tai lieu.

### 10.5 Branch

Branch la con tro toi commit.

Tao branch:

```bash
git checkout -b feature/home-austin-setup
```

Nghia la tao branch moi va switch sang branch do.

### 10.6 main

`main` la branch chinh cua repo. Thuong duoc protect, khong push truc tiep.

Ve main:

```bash
git checkout main
```

Cap nhat main:

```bash
git pull
```

### 10.7 origin

`origin` la ten mac dinh cua remote repo.

Trong result:

```text
origin git@github.com:trunganhxxiiidev/be-fast-api-training-trainee.git
```

Nghia la remote GitHub nam o dia chi SSH do.

Xem remote:

```bash
git remote -v
```

### 10.8 SSH key

SSH key giup may cua ban xac thuc voi GitHub ma khong can go password moi lan push.

Kiem tra key:

```bash
ls -lah ~/.ssh
```

Test GitHub SSH:

```bash
ssh -T git@github.com
```

Neu thanh cong co the thay message dai loai:

```text
Hi <username>! You've successfully authenticated...
```

### 10.9 Push

Push day commit tu may local len remote.

```bash
git push -u origin feature/home-austin-setup
```

Giai thich:

| Phan | Nghia |
|---|---|
| `git push` | Day commit len remote |
| `-u` | Set upstream tracking |
| `origin` | Remote |
| `feature/home-austin-setup` | Branch can push |

Sau khi set upstream, lan sau chi can:

```bash
git push
```

### 10.10 Upstream / tracking branch

Trong result:

```text
branch 'feature/home-austin-setup' set up to track 'origin/feature/home-austin-setup'
```

Nghia la local branch da lien ket voi remote branch. Git biet push/pull tu dau.

Kiem tra:

```bash
git branch -vv
```

### 10.11 Pull Request

PR la yeu cau merge branch vao main. PR giup review code truoc khi merge.

PR URL trong result:

```text
https://github.com/trunganhxxiiidev/be-fast-api-training-trainee/pull/new/feature/home-austin-setup
```

### 10.12 Git identity

Git can biet ten/email de ghi vao commit.

Error trong result:

```text
Author identity unknown
fatal: unable to auto-detect email address
```

Fix local trong repo:

```bash
git config user.name "trunganhxxiiidev"
git config user.email "trunganhxxiiidev@users.noreply.github.com"
```

Fix global cho tat ca repo:

```bash
git config --global user.name "trunganhxxiiidev"
git config --global user.email "trunganhxxiiidev@users.noreply.github.com"
```

Xem config:

```bash
git config --list
git config --get user.name
git config --get user.email
```

### 10.13 Amend

Trong result co:

```text
commit was amended once
```

`git commit --amend` sua commit cuoi cung. Dung khi vua commit xong nhung muon them file/sua message/sua noi dung.

Vi du:

```bash
git add journal/day-01.md
git commit --amend --no-edit
```

Neu commit da push, amend lam hash doi. Can push:

```bash
git push --force-with-lease
```

`--force-with-lease` an toan hon `--force` vi no kiem tra remote co bi nguoi khac update khong.

### 10.14 Merge vs rebase

Merge:

```bash
git checkout main
git merge feature/home-austin-setup
```

Giu lich su branch, co the tao merge commit.

Rebase:

```bash
git checkout feature/home-austin-setup
git rebase main
```

Dat commit cua branch hien tai len tren main moi nhat. Lich su nhin gon hon, nhung co the rewrite history.

Quy tac:

```text
Rebase branch ca nhan: OK
Rebase branch da share voi team: can than
Merge vao branch chung: an toan hon
```

## 11. Conventional Commits

Format:

```text
type: description
```

Vi du:

```text
docs: add day 01 setup journal
feat: add user login API
fix: handle missing token
test: add auth service tests
refactor: simplify user repository
chore: update dependencies
```

Type hay gap:

| Type | Dung khi |
|---|---|
| `feat` | Them feature |
| `fix` | Sua bug |
| `docs` | Sua tai lieu |
| `test` | Them/sua test |
| `refactor` | Doi code khong doi behavior |
| `chore` | Viec phu: config, dependency, tooling |
| `style` | Format, whitespace, khong doi logic |
| `perf` | Cai thien performance |

## 12. Cac Lenh Help Nen Hoc

Linux co nhieu cach tu xem huong dan.

### 12.1 `--help`

```bash
ls --help
find --help
grep --help
tail --help
git --help
```

Nhanh, hien option co ban.

### 12.2 `man`

```bash
man ls
man find
man grep
man tail
man git
```

`man` la manual page day du hon.

Trong man:

| Phim | Chuc nang |
|---|---|
| `q` | Thoat |
| `/text` | Tim text |
| `n` | Ket qua tiep theo |
| `Space` | Xuong trang |

### 12.3 `type`, `command -v`, `which`

```bash
type python
type -a python
command -v python
which python
```

Nen uu tien:

```bash
command -v <cmd>
type -a <cmd>
```

Vi day la builtin cua shell, dang tin hon trong viec xem shell that su se chay cai gi.

## 13. Bai Tap Copy De Thuc Hanh That

Tat ca bai tap duoi day chay trong folder rieng, an toan hon.

### 13.1 Tao folder practice

```bash
mkdir -p ~/Training/day01-shell-practice
cd ~/Training/day01-shell-practice
pwd
```

### 13.2 Tao file mau

```bash
cat > README.md <<'EOF'
# Day 01 Practice

TODO: learn shell commands
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9
Line 10
Line 11
EOF

mkdir -p logs src
cat > src/app.py <<'EOF'
print("hello day 01")
EOF

cat > logs/app.log <<'EOF'
log line 1
log line 2
log line 3
EOF
```

### 13.3 Navigation practice

```bash
pwd
ls -lah
tree -L 2
cd src
pwd
cd ..
pwd
```

Tu hoi:

```text
Minh dang o folder nao?
Folder hien tai co file gi?
Thu muc cha la gi?
```

### 13.4 Find practice

```bash
find . -name "*.py"
find . -type f -name "*.md"
find . -type f
find . -type d
```

Tu hoi:

```text
find dang bat dau tim tu dau?
-type f va -type d khac nhau the nao?
*.py can dat trong quote vi sao?
```

### 13.5 Grep practice

```bash
grep "TODO" README.md
grep -n "TODO" README.md
grep -rni "todo" .
grep -rni "hello" .
```

Tu hoi:

```text
-r de lam gi?
-n de lam gi?
-i de lam gi?
```

### 13.6 Head/tail/wc practice

```bash
head -n 5 README.md
tail -n 5 README.md
wc -l README.md
wc -w README.md
wc -c README.md
```

### 13.7 Pipe and redirect practice

```bash
ls -lah > files.txt
echo "new line" >> files.txt
cat files.txt
find . -name "*.py" | wc -l
find . -name "*.log" | xargs tail -n 20
```

Tu hoi:

```text
> va >> khac nhau the nao?
Pipe dua output tu dau sang dau?
xargs bien input thanh gi?
```

### 13.8 Process/port practice

Mo mot server tam tren port 8000:

```bash
cd ~/Training/day01-shell-practice
python -m http.server 8000
```

Mo terminal khac va chay:

```bash
lsof -i :8000
ps aux | grep "http.server"
```

Dung server:

```bash
kill <PID>
```

Neu muon lay PID nhanh:

```bash
lsof -ti :8000
kill "$(lsof -ti :8000)"
```

### 13.9 pyenv practice

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

pyenv --version
pyenv versions
pyenv version
pyenv which python
python --version
```

Tao project dung Python rieng:

```bash
mkdir -p ~/Training/day01-pyenv-practice
cd ~/Training/day01-pyenv-practice
pyenv local 3.12.13
cat .python-version
python --version
```

### 13.10 uv practice

```bash
mkdir -p ~/Training/day01-uv-practice
cd ~/Training/day01-uv-practice
uv venv
source .venv/bin/activate
uv pip install requests
python -c "import requests; print(requests.__version__)"
deactivate
```

Xem thu muc:

```bash
tree -L 2
```

### 13.11 Git practice an toan trong repo tam

Dung repo tam de hieu flow, khong anh huong repo that:

```bash
rm -rf /tmp/day01-git-practice /tmp/day01-git-remote.git
mkdir -p /tmp/day01-git-practice
cd /tmp/day01-git-practice

git init -b main
git config user.name "practice-user"
git config user.email "practice@example.local"

echo "# Practice Repo" > README.md
git add README.md
git commit -m "chore: initial commit"

git init --bare /tmp/day01-git-remote.git
git remote add origin /tmp/day01-git-remote.git
git push -u origin main

git checkout main
git pull
git checkout -b feature/day-01-practice

mkdir -p journal
echo "# Day 01 Journal" > journal/day-01.md
git status
git add journal/day-01.md
git commit -m "docs: add day 01 journal"
git push -u origin feature/day-01-practice

git log --oneline --graph --all
```

Tu hoi:

```text
git add dua file vao dau?
git commit tao cai gi?
git push day commit di dau?
origin la gi?
branch feature/day-01-practice khac main nhu the nao?
```

### 13.12 Git practice tren repo training that

Chi chay khi ban muon xem, khong tao commit moi:

```bash
cd /home/home-austin/Training/D1/be-fast-api-training-trainee
git status --short --branch
git remote -v
git branch -vv
git log --oneline --graph --all -n 10
```

Khong chay commit/push neu chua chac.

## 14. Checklist Tu Hoc Lai

Danh dau khi ban tu giai thich duoc:

```text
[ ] ~ la gi
[ ] PATH la gi
[ ] .bashrc dung de lam gi
[ ] .profile khac .bashrc o diem nao
[ ] python he thong khac pyenv Python nhu the nao
[ ] pyenv shim la gi
[ ] uv dung de lam gi
[ ] virtual environment la gi
[ ] find -name "*.py" hoat dong ra sao
[ ] grep -rni nghia la gi
[ ] tail -f dung khi nao
[ ] wc -l dung de dem gi
[ ] pipe | truyen du lieu the nao
[ ] > va >> khac nhau the nao
[ ] 2>/dev/null nghia la gi
[ ] lsof -i :8000 dung de xem gi
[ ] git working tree la gi
[ ] git staging area la gi
[ ] commit la gi
[ ] branch la gi
[ ] remote origin la gi
[ ] push -u co tac dung gi
[ ] PR la gi
[ ] merge khac rebase nhu the nao
```

## 15. Cach Hoc Command Moi

Moi khi gap mot command moi, dung format nay:

```text
1. Command ten gi?
2. No doc du lieu tu dau?
3. No ghi output ra dau?
4. No co sua/xoa file khong?
5. Option nao dang duoc dung?
6. Neu chay sai co nguy hiem khong?
7. Co cach xem help khong?
```

Vi du voi:

```bash
find ~ -name "*.py" 2>/dev/null | wc -l
```

Tra loi:

```text
1. Command chinh: find, wc.
2. find doc cay thu muc tu ~.
3. find in danh sach file ra stdout.
4. wc doc danh sach do qua pipe va dem dong.
5. -name loc theo ten; -l dem dong.
6. Khong sua/xoa file, an toan.
7. Xem help bang find --help, wc --help, man find.
```

## 16. Loi Hay Gap Va Cach Doc

### 16.1 Command not found

```text
python: command not found
```

Nghia la shell khong tim thay executable `python` trong PATH.

Fix co the la:

```bash
sudo apt install python-is-python3
```

Hoac init pyenv:

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

### 16.2 Not a Git repository

```text
fatal: not a git repository
```

Nghia la folder hien tai khong co `.git`.

Fix:

```bash
cd /path/to/repo
git status
```

### 16.3 Author identity unknown

```text
Author identity unknown
```

Nghia la Git chua biet name/email de ghi commit.

Fix local:

```bash
git config user.name "your-name"
git config user.email "your-email@example.com"
```

Fix global:

```bash
git config --global user.name "your-name"
git config --global user.email "your-email@example.com"
```

### 16.4 Permission denied

Neu gap:

```text
Permission denied
```

Co the do:

1. File/folder khong co quyen doc/ghi.
2. SSH key chua dung.
3. Command can sudo.

Debug:

```bash
ls -lah
whoami
id
ssh -T git@github.com
```

## 17. Lenh Nen Thuong Xuyen Dung Khi Lam Backend

File/project:

```bash
pwd
ls -lah
tree -L 2
find . -type f -name "*.py"
grep -rni "TODO" .
```

Python:

```bash
python --version
pyenv version
uv --version
uv venv
source .venv/bin/activate
uv pip install fastapi uvicorn
```

Server/process:

```bash
lsof -i :8000
ps aux | grep uvicorn
kill <PID>
```

Git:

```bash
git status --short --branch
git branch -vv
git remote -v
git log --oneline --graph --all -n 10
git add <file>
git commit -m "docs: update journal"
git push
```

Help:

```bash
<command> --help
man <command>
type -a <command>
command -v <command>
```

## 18. Ban Tom Tat Sieu Ngan

```text
pyenv = quan ly version Python.
uv = tool nhanh de tao env/cai package/chay Python project.
.bashrc = config cho Bash terminal moi.
.profile = config cho login shell.
PATH = danh sach folder shell dung de tim command.
find = tim file.
grep = tim text.
tail = xem cuoi file/log.
lsof = xem process dang mo file/port.
pipe | = noi output command nay vao input command kia.
git add = dua thay doi vao staging.
git commit = tao snapshot.
git push = day commit len remote.
PR = yeu cau merge branch vao main.
```

