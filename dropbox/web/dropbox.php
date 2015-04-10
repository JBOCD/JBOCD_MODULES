<?php

# Include the Dropbox SDK libraries
require_once  APPPATH . "third_party/dropbox/lib/Dropbox/autoload.php";
use \Dropbox as dbx;

class Dropbox {

	protected $lid;
	protected $db;
	protected $statusCode;
	protected $webAuth;
	public $name = "Dropbox";

	public function __construct($db){
		$appInfo = dbx\AppInfo::loadFromJsonFile(APPPATH."third_party/dropbox/appinfo.json");
		$this->webAuth = new dbx\WebAuth($appInfo, "PCL1401", str_replace('http://', 'https://', site_url('main/returnAdd/dropbox')), new dbx\ArrayEntryStore($_SESSION, 'dropbox-auth-csrf-token'));
		$this->statusCode = array('Deactivated', 'Normal', 'Disabled');
		if(!isset($db) || $db == null) return false;
		$this->db = $db;

		if($q = $this->db->query("SELECT * FROM `libraries` WHERE `dir` = 'dropbox'")){
			if ($q->num_rows() > 0){
				$row = $q->row();
			}else{
				throw new Exception("Cannot find dropbox library record in database.", 1);
			}
			$this->lid = $row->id;
		}
	}
	
	public function getAccountView($uid){
		$result = $this->db->query('SELECT * FROM `dropbox` WHERE `id` IN (SELECT `cdid` FROM `clouddrive` WHERE `uid` = ? AND `lid` = ?)', array($uid, $this->lid));
		if($result->num_rows() <= 0){
			$account = false;
		}else{
			$account = array();
			foreach($result->result_array() as $row){
				if($row['status']==1){
					try{
						$dbxClient = new dbx\Client($row['key'], "PCL1401");
						$accountInfo = $dbxClient->getAccountInfo();
					}catch(Exception $e){
						$this->dise($row['id']);
					}
					array_push($account, array(
						'id'=>$row['id'], 
						'name'=>$row['name'],
						'status'=>$this->statusCode[$row['status']], 
						'quota'=>round($accountInfo['quota_info']['quota'] / 1073741824, 2, PHP_ROUND_HALF_DOWN),
						'available'=>round(($accountInfo['quota_info']['quota'] - $accountInfo['quota_info']['normal'] - $accountInfo['quota_info']['shared']) / 1073741824,2,PHP_ROUND_HALF_DOWN),
						'action'=>'<a href="'.site_url('main/delAccount/dropbox/'.$row['id']).'"><i class="icon-remove fg-white"></i></a>'));
				}else{
					array_push($account, 
						array(
							'id'=>$row['id'], 
							'name'=>$row['name'], 
							'status'=>$this->statusCode[$row['status']], 
							'quota'=>"---",
							'available'=>"---",
							'action'=>'<a href="'.site_url('main/delAccount/dropbox/'.$row['id']).'"><i class="icon-remove fg-white"></i></a>'));
				}
			}
		}
		return array(
			'title'=>$this->name,
			'dir'=>'dropbox',
			'thead'=>array('ID', 'User Name', 'User ID', 'Status', 'Quota (GB)', 'Available (GB)', 'Action'),
			'tbody'=>$account
		);
	}
	
	public function auth(){
		$authorizeUrl = $this->webAuth->start();
		redirect($authorizeUrl, 'refresh');
	}
	
	public function remv($id){
		$result = $this->db->query('SELECT * FROM dropbox WHERE id = ?', array($id));
		if($result->num_rows() == 1){
			$row = $result->row();
			$dbxClient = new dbx\Client($row->key, "PCL1401");
			$dbxClient->disableAccessToken();
			$this->db->trans_start();
			$this->db->delete('dropbox', array('id' => $id));
			$this->db->delete('clouddrive', array('cdid' => $id));
			$this->db->trans_complete();
			if ($this->db->trans_status() === FALSE){
				echo "This transaction goes wrong!";
				return false;
			}
		}
		redirect('main/module/dropbox');
	}
	
	public function dise($id){
		$result = $this->db->query('SELECT * FROM dropbox WHERE id = ?', array($id));
		if($result->num_rows() == 1){
			$row = $result->row();
			$this->db->trans_start();
			$this->db->update('dropbox', array('status'=>0), array('id' => $id));
			$this->db->trans_complete();
			if ($this->db->trans_status() === FALSE){
				echo "This transaction goes wrong!";
				return false;
			}
		}
		redirect('main/module/dropbox');
	}
	
	public function proc($request, $uid){
		list($accessToken, $dropboxUserId, $urlState) = $this->webAuth->finish($request);
		try{
			$dbxClient = new dbx\Client($accessToken, "PCL1401");
			$accountInfo = $dbxClient->getAccountInfo();
			$this->db->trans_start();
			$this->db->replace('clouddrive', array('lid'=>$this->lid, 'uid'=>$uid));
			$this->db->replace('dropbox', array('id'=>$this->db->insert_id(),'key'=>$accessToken, 'userid'=>$dropboxUserId, 'status'=>1, 'name'=>$accountInfo['display_name']));
			$this->db->trans_complete();
		}catch(Exception $e){
			$this->dise($row['id']);
		}
		if ($this->db->trans_status() === FALSE){
			echo "This transaction goes wrong!";
			return false;
		}
		redirect('main/module/dropbox');
	}

	public function distroy(){
		$result = $this->db->query('SELECT * FROM `dropbox`');
		if($result->num_rows() > 0){
			foreach($result->result_array() as $row){
				$this->remv($id);
			}
		}
		$this->db->query('DROP TABLE IF EXISTS `dropbox`');
		$this->db->query('DELETE FROM `libraries` WHERE `dir` = ?', array('dropbox'));
		return true;
	}

	public function getDrivesInfo($id){
		$result = $this->db->query('SELECT * FROM `dropbox` WHERE `id` = ?', array($id));
		try{
			$row = $result->row();
			$dbxClient = new dbx\Client($row->key, "PCL1401");
			$accountInfo = $dbxClient->getAccountInfo();
			return array(
				'id'=>$id,
				'quota'=>round($accountInfo['quota_info']['quota'] / 1073741824, 2, PHP_ROUND_HALF_DOWN), 
				'available'=>round(($accountInfo['quota_info']['quota'] - $accountInfo['quota_info']['normal'] - $accountInfo['quota_info']['shared']) / 1073741824,2,PHP_ROUND_HALF_DOWN), 
				'name'=>$row->name,
				'status'=>true);
		}catch(Exception $e){
			//$this->dise($row['id']);
			return array(
				'id'=>$id,
				'quota'=>0, 
				'available'=>0, 
				'name'=>$row->name,
				'status'=>false);;
		}
	}

	public function rmdir($dir, $id){
		try{
			$result = $this->db->query('SELECT * FROM `dropbox` WHERE `id` = ?', array($id));
			$row = $result->row();
			$dbxClient = new dbx\Client($row->key, "PCL1401");
			$dbxClient->delete($dir);
		}catch(Exception $e){
			return false;
		}
	}

}
?>