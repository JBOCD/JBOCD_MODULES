<?php 

# Include the Google Library
require_once APPPATH.'third_party/googledrive/src/Google_Client.php';
require_once APPPATH.'third_party/googledrive/src/contrib/Google_Oauth2Service.php';
require_once APPPATH.'third_party/googledrive/src/contrib/Google_DriveService.php';

# Create new instance of Google class
$client = new Google_Client();

class Googledrive {

	public $name = "Google Drive";

	private $client;
	private $drive;

	protected $lid;
	protected $db;
	protected $statusCode;
	
	public function __construct($db = null){
		$this->db = $db;
	
		# Create new instance of Google class
		$this->client = new Google_Client();
		# Get your credentials from the console
		$this->client->setClientId('1057260143746-nunu5nj337r77e2etcknaa1p9rtpmgvs.apps.googleusercontent.com');
		$this->client->setClientSecret('bAblGSZpt2VfCekWDvujMS-g');
		$this->client->setRedirectUri('urn:ietf:wg:oauth:2.0:oob');
		$this->client->setScopes(array('https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email'));
		$this->client->setRedirectUri(urldecode(str_replace('http://', 'https://', site_url('main/returnAdd/googledrive'))));
		
		$this->statusCode = array('Deactivated', 'Normal', 'Disabled');

		if($q = $this->db->query("SELECT * FROM `libraries` WHERE `dir` = 'googledrive'")){
			if ($q->num_rows() > 0){
				$row = $q->row();
			}else{
				throw new Exception("Cannot find google drive library record in database.", 1);
			}
			$this->lid = $row->id;
		}
	}
	
	public function getAccountView($uid){
		$result = $this->db->query('SELECT * FROM `googledrive` WHERE `id` IN (SELECT `cdid` FROM `clouddrive` WHERE `uid` = ? AND `lid` = ?)', array($uid, $this->lid));
		if($result->num_rows() <= 0){
			$account = false;
		}else{
			$account = array();
			foreach($result->result_array() as $row){
				$apiClient = new Google_Client();
				$apiClient->setUseObjects(true);
				$apiClient->setAccessToken($row['key']);
				$drive = new Google_DriveService($apiClient);
				if($row['status']==1){
					try{
						$about = $drive->about->get();
						array_push($account, 
							array(
								'id'=>$row['id'], 
								'name'=>$row['userid'], 
								'status'=>$this->statusCode[$row['status']], 
								'quota'=>round($about->getQuotaBytesTotal()/1073741824, 2, PHP_ROUND_HALF_DOWN),
								'available'=>round(($about->getQuotaBytesTotal()-$about->getQuotaBytesUsed())/1073741824, 2, PHP_ROUND_HALF_DOWN),
								'action'=>'<a href="'.site_url('main/delAccount/googledrive/'.$row['id']).'"><i class="icon-remove fg-white"></i></a>'));
					}catch(Google_ServiceException $e){
						$this->dise($row['id']);
					}
				}else{
					array_push($account, 
						array(
							'id'=>$row['id'], 
							'name'=>$row['userid'], 
							'status'=>$this->statusCode[$row['status']], 
							'quota'=>"---",
							'available'=>"---",
							'action'=>'<a href="'.site_url('main/delAccount/googledrive/'.$row['id']).'"><i class="icon-remove fg-white"></i></a>'));
				}
			}
		}
		return array(
			'title'=>$this->name,
			'dir'=>'googledrive',
			'thead'=>array('ID', 'User ID', 'Status', 'Quota (GB)', 'Available (GB)', 'Action'),
			'tbody'=>$account
		);
	}
	
	public function auth(){
		$authorization = $this->client;
		$authorization->setAccessType('offline');
		$authorization->setRedirectUri(urldecode(str_replace('http://', 'https://', site_url('main/returnAdd/googledrive'))));
		$authorization->setApprovalPrompt('force');
		redirect($this->client->createAuthUrl(), 'refresh');
	}
	
	public function remv($id){
		$result = $this->db->query('SELECT * FROM googledrive WHERE id = ?', array($id));
		if($result->num_rows() == 1){
			$row = $result->row();
			$apiClient = new Google_Client();
			$apiClient->setUseObjects(true);
			$apiClient->setAccessToken($row->key);
			$drive = new Google_DriveService($apiClient);
			try{
				$about = $drive->about->get();
				$auth = $apiClient->getAuth();
				$auth->revokeToken();
			}catch(Google_ServiceException $e){
			}catch(Google_AuthException $e){
			}
			$this->db->trans_start();
			$this->db->delete('googledrive', array('id' => $id));
			$this->db->delete('clouddrive', array('cdid' => $id));
			$this->db->trans_complete();
			if ($this->db->trans_status() === FALSE){
				echo "This transaction goes wrong!";
				return false;
			}
		}
		redirect('main/module/googledrive');
	}
	
	public function dise($id){
		$result = $this->db->query('SELECT * FROM googledrive WHERE id = ?', array($id));
		if($result->num_rows() == 1){
			$row = $result->row();
			$this->db->trans_start();
			$this->db->update('googledrive', array('status'=>0), array('id' => $id));
			$this->db->trans_complete();
			if ($this->db->trans_status() === FALSE){
				echo "This transaction goes wrong!";
				return false;
			}
		}
		redirect('main/module/googledrive');
	}
	
	public function proc($request, $uid){
		
		$this->client->setRedirectUri(urldecode(str_replace('http://', 'https://', site_url('main/returnAdd/googledrive'))));
		$credentials = $this->client->authenticate();
		$apiClient = new Google_Client();
		$apiClient->setUseObjects(true);
		$apiClient->setAccessToken($credentials);
		$userInfoService = new Google_Oauth2Service($apiClient);
		$userInfo = $userInfoService->userinfo->get();
		if($userInfo == null) throw new NoUserIdException("Cannot get user information!");

		$q = $this->db->query("SELECT * FROM `googledrive` WHERE `userid` = ?", array($userInfo->email));
		$this->db->trans_start();
		$this->db->replace('clouddrive', array('lid'=>$this->lid, 'uid'=>$uid));
		$this->db->replace('googledrive', array('id'=>$this->db->insert_id(), 'key'=>$credentials, 'userid'=>$userInfo->email, 'status'=>1));
		$this->db->trans_complete();
		if ($this->db->trans_status() === FALSE){
			echo "This transaction goes wrong!";
			return false;
		}
		redirect('main/module/googledrive');
	}
	
	public function distroy(){
		$result = $this->db->query('SELECT * FROM `googledrive`');
		if($result->num_rows() > 0){
			foreach($result->result_array() as $row){
				$this->remv($row['id']);
			}
		}
		$this->db->query('DROP TABLE IF EXISTS `googledrive`');
		$this->db->query('DELETE FROM `libraries` WHERE `dir` = ?', array('googledrive'));
		return true;
	}
	
}

?>