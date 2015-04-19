<?php

class Ftp {

	protected $lid;
	protected $db;
	protected $statusCode;
	public $name = "FTP";

	public function __construct($db){
		$this->statusCode = array('Deactivated', 'Normal', 'Disabled');
		if(!isset($db) || $db == null) return false;
		$this->db = $db;

		if($q = $this->db->query("SELECT * FROM `libraries` WHERE `dir` = 'ftp'")){
			if ($q->num_rows() > 0){
				$row = $q->row();
			}else{
				throw new Exception("Cannot find ftp library record in database.", 1);
			}
			$this->lid = $row->id;
		}
	}
	
	public function getAccountView($uid){
		$result = $this->db->query('SELECT * FROM `ftp` WHERE `id` IN (SELECT `cdid` FROM `clouddrive` WHERE `uid` = ? AND `lid` = ?)', array($uid, $this->lid));
		if($result->num_rows() <= 0){
			$account = false;
		}else{
			$account = array();
			foreach($result->result_array() as $row){
				$info = json_decode($row['key'], true);
				array_push($account,
					array(
						'id'=>$row['id'],
						'name'=>$info['user'].'@'.$info['host'].($info['port'] != 21 ? ':'.$info['port'] : ''),
						'status'=>$this->statusCode[1],
						'quota'=>$info['quota'],
						'available'=>$info['quota'],
						'action'=>'<a href="'.site_url('main/delAccount/ftp/'.$row['id']).'"><i class="icon-remove fg-white"></i></a>'
					)
				);
 			}
		}
		return array(
			'title'=>$this->name,
			'dir'=>'ftp',
			'thead'=>array('ID', 'User Name', 'User ID', 'Status', 'Quota (GB)', 'Available (GB)', 'Action'),
			'tbody'=>$account
		);
	}
	
	public function auth(){
		return array(
			'name'=>'FTP',
			'dir'=>'ftp',
			'form'=>array(
				array(
					'type'=>'checkbox',
					'name'=>'isSecure',
					'value'=>true,
					'description'=>'Use Secure Connection?'
				),
				array(
					'type'=>'text',
					'name'=>'host',
					'placeholder'=>'ftp.cuhk.edu.hk',
					'pattern'=>'^([\w\d-_]+\.)+[\w\d-_]+$',
					'title'=>'Please Enter valid Host name or IP address',
					'description'=>'Host IP or Host name',
					'required'=>true
				),
				array(
					'type'=>'number',
					'name'=>'port',
					'placeholder'=>'0-65535',
					'min'=>0,
					'max'=>65535,
					'title'=>'Range from 0 to 65535',
					'description'=>'Port number'
				),
				array(
					'type'=>'text',
					'name'=>'ac',
					'placeholder'=>'Login ID',
					'required'=>true
				),
				array(
					'type'=>'password',
					'name'=>'pw',
					'placeholder'=>'Login Password',
				),
				array(
					'type'=>'text',
					'name'=>'quota',
					'pattern'=>'\d+(\.\d+)?',
					'description'=>'GB, Total size for JBOCD use',
					'required'=>true
				)
			)
		);
	}

	public function remv($id){
		$result = $this->db->query('SELECT * FROM ftp WHERE id = ?', array($id));
		if($result->num_rows() == 1){
			$row = $result->row();
			$this->db->trans_start();
			$this->db->delete('ftp', array('id' => $id));
			$this->db->delete('clouddrive', array('cdid' => $id));
			$this->db->trans_complete();
			if ($this->db->trans_status() === FALSE){
				echo "This transaction goes wrong!";
				return false;
			}
		}
		redirect('main/module/ftp');
	}

	public function proc($req, $uid){
		$this->db->trans_start();
		$this->db->insert('clouddrive', array('lid'=>$this->lid, 'uid'=>$uid));
		$this->db->insert('ftp', array(
			'id'=>$this->db->insert_id(),
			'key'=>json_encode(array(
				'host'=>$req['host'],
				'port'=>(isset($req['port']) && is_numeric($req['port']) && (int) $req['port'] >= 0 && (int)$req['port'] <= 65535 ? (int)$req['port'] : 21),
				'user'=>$req['ac'],
				'pass'=>$req['pw'],
				'secure'=>isset($req['secure']) && $req['secure'],
				'quota'=>(float)$req['quota']
			))
		));
		$this->db->trans_complete();
		if ($this->db->trans_status() === FALSE){
			echo "This transaction goes wrong!";
			return false;
		}
		redirect('main/module/ftp');
	}

	public function distroy(){
		$result = $this->db->query('SELECT * FROM `ftp`');
		if($result->num_rows() > 0){
			foreach($result->result_array() as $row){
				$this->remv($row->id);
			}
		}
		$this->db->query('DROP TABLE IF EXISTS `ftp`');
		$this->db->query('DELETE FROM `libraries` WHERE `dir` = "ftp"');
		return true;
	}

	public function getDrivesInfo($id){
		$result = $this->db->query('SELECT * FROM `ftp` WHERE `id` = ?', array($id));
		$row = $result->row();
		$info = json_decode($row->key);
		return array(
			'id'=>$id,
			'quota'=>round($info->quota, 2, PHP_ROUND_HALF_DOWN),
			'available'=>round($info->quota,2,PHP_ROUND_HALF_DOWN),
			'name'=>$info->user.'@'.$info->host.($info->port != 21 ? ':'.$info->port : ''),
			'status'=>true);
	}

	public function rmdir($dir, $id){
		try{
			$result = $this->db->query('SELECT * FROM `dropbox` WHERE `id` = ?', array($id));
			$row = $result->row();
			$info = json_decode($row->key);
			$ftp = $row->secure ? ftp_ssl_connect($row->host, $row->port) : ftp_connect($row->host, $row->port);
			ftp_login($ftp, $row->user, $row->pass);
			ftp_delete($ftp, $dir);
			ftp_quit($ftp);
		}catch(Exception $e){
		}
	}

}
?>
