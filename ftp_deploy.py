import ftplib
import io
import requests

def upload_via_ftp():
    host = "66.152.169.178"
    user = "hsapi_xyz"
    passwd = "Q2W3EEPA8DDP"
    
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, 21, timeout=30)
        ftp.login(user, passwd)
        print("FTP 登录成功！")
        
        # 建立 logos 目录
        try:
            ftp.mkd("/logos")
        except:
            pass
            
        logos = {
            "644.png": "https://img.vipsoccer.com/soccer/team/644.png",
            "654.png": "https://img.vipsoccer.com/soccer/team/654.png",
            "653.png": "https://img.vipsoccer.com/soccer/team/653.png",
            "651.png": "https://img.vipsoccer.com/soccer/team/651.png"
        }
        
        for filename, url in logos.items():
            print(f"正在通过 FTP 推送 {filename}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bio = io.BytesIO(response.content)
                ftp.storbinary(f"STOR /logos/{filename}", bio)
                print(f"{filename} 上传完成！")
        
        ftp.quit()
        return True
    except Exception as e:
        print(f"FTP 错误: {e}")
        return False

if __name__ == "__main__":
    upload_via_ftp()
