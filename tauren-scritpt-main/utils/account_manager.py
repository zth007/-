"""
账号管理模块
"""
import json
import os

class Account:
    """账号类"""
    def __init__(self, account_id, name, cookie_file, status="inactive", operation_count=0, last_used=None):
        self.account_id = account_id
        self.name = name
        self.cookie_file = cookie_file
        self.status = status
        self.operation_count = operation_count
        self.last_used = last_used

class AccountManager:
    """账号管理器"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AccountManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, accounts_file=None):
        if not hasattr(self, "_initialized"):
            if accounts_file is None:
                # 使用绝对路径
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.accounts_file = os.path.join(base_dir, "data", "accounts.json")
            else:
                self.accounts_file = accounts_file
            self.accounts = self._load_accounts()
            self._initialized = True
    
    def _load_accounts(self):
        """加载账号配置"""
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                accounts = []
                for acc in data.get('accounts', []):
                    account = Account(
                        account_id=acc.get('account_id'),
                        name=acc.get('name'),
                        cookie_file=acc.get('cookie_file'),
                        status=acc.get('status', 'inactive'),
                        operation_count=acc.get('operation_count', 0),
                        last_used=acc.get('last_used')
                    )
                    accounts.append(account)
                return accounts
            else:
                return []
        except Exception as e:
            print(f"加载账号配置失败: {e}")
            return []
    
    def _save_accounts(self):
        """保存账号配置"""
        try:
            os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)
            data = {
                'accounts': [
                    {
                        'account_id': acc.account_id,
                        'name': acc.name,
                        'cookie_file': acc.cookie_file,
                        'status': acc.status
                    }
                    for acc in self.accounts
                ]
            }
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存账号配置失败: {e}")
    
    def add_account(self, name, cookie_file):
        """添加账号"""
        account_id = f"account_{len(self.accounts) + 1}"
        account = Account(account_id, name, cookie_file)
        self.accounts.append(account)
        self._save_accounts()
        return account
    
    def update_account(self, account_id, **kwargs):
        """更新账号"""
        for account in self.accounts:
            if account.account_id == account_id:
                for key, value in kwargs.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                self._save_accounts()
                return True
        return False
    
    def delete_account(self, account_id):
        """删除账号"""
        for i, account in enumerate(self.accounts):
            if account.account_id == account_id:
                self.accounts.pop(i)
                self._save_accounts()
                return True
        return False
    
    def get_status(self):
        """获取账号状态"""
        return {
            'total': len(self.accounts),
            'accounts': [
                {
                    'account_id': acc.account_id,
                    'name': acc.name,
                    'cookie_file': acc.cookie_file,
                    'status': acc.status,
                    'operation_count': getattr(acc, 'operation_count', 0),
                    'last_used': getattr(acc, 'last_used', None)
                }
                for acc in self.accounts
            ]
        }

# 全局账号管理器实例
account_manager = AccountManager()