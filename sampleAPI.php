<?php

$servername = "localhost";
$username = "iotdev";
$password = "iotdb190";
$dbname = "iotdb";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
    echo "no access";
} 

// for now BLE is a post so we need to run a bit different with JSON from the IOT
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // looks like we have a POST rather than a get. lets parse the JSON
    $dPost = file_get_contents('php://input');
    $jdd = json_decode($dPost,true);
    
    $cmd = $jdd["cmd"];
    $mac = $jdd["mac"];
    
    // debug cmd
    //echo "{\"cmd\":\"".$cmd."\"}";
    
    if ($cmd=="REG") {
        
        $ip = $jdd["ip"];
        $hw = $jdd["hw"];
        $swver = $jdd["swver"];
    
        // check if its a first time registration by looking for the mac in the device table
        $sql = "SELECT * FROM devices WHERE mac='".$mac."'";
        
        $srch = $conn->query($sql);
        
        if ($srch->num_rows > 0) {
            if ($row = $srch->fetch_assoc()) {
                $sql = "UPDATE devices SET lastseen=now(), ip='".$ip."', swver='".$swver."', hw='".$hw."' WHERE devID='".$row['devID']."'";
                // update record
                $r = $conn->query($sql);
                //echo "{\"resp\":\"".$sql."\"}";
                echo "{\"resp\":\"UPDATED\"}";
            }
        }
        else {
            // mac not there, let's see if it's a new registration 
            // are we registering a thing?
            if ($mac!="") {

                // we need to inset a new registration
                $sql = "INSERT INTO devices("
                        . "lastseen, "
                        . "mac, "
                        . "ip, "
                        . "swver, "
                        . "status, "
                        . "hw) "
                        . "VALUES (now(), '".$mac."', '".$ip."', '".$swver."', 'ACTIVE', '".$hw."')";

                $r = $conn->query($sql);
                //echo "{\"resp\":\"".$sql."\"}";
                echo "{\"resp\":\"NEW\"}";
            }

            else {
                // no tagID matching our database
                echo "{\"resp\":\"ERROR\"}";

            }
            
        }
        
    }

    if ($cmd=="LIST") {
        $sql = "SELECT * FROM devices" ;
        $srch = $conn->query($sql);
        
        if ($srch->num_rows > 0) {
            $first = true;
            echo '{"devices" : [';
            while($t = $srch->fetch_assoc()) {
                if ($first==false)
                    echo ",";
                $rowJSON = json_encode($t);
                echo $rowJSON;
                $first=false;
            }
            echo ']}';

        } // end of rows found

    } // end of LIST command
   
    if ($cmd=="GROUPS") {
        
        $gid = $jdd["gid"];

        if (empty($gid)) {
            $sql = "SELECT * FROM groups" ;
        }
        else {
            $sql = "SELECT * FROM groups WHERE groupID='".$gid."'" ;
        }
        $srch = $conn->query($sql);
        
        if ($srch->num_rows > 0) {
            $first = true;
            echo '{"groups" : [';
            while($t = $srch->fetch_assoc()) {
                if ($first==false)
                    echo ",";
                $rowJSON = json_encode($t);
                echo $rowJSON;
                $first=false;
            }
            echo ']}';

        } // end of rows found

    } // end of GROUPS command
} // end of post call

// we got a GET ?
if ($_SERVER['REQUEST_METHOD'] === 'GET') {

 	$cmd = filter_input(INPUT_GET, "cmd", FILTER_SANITIZE_STRING);
    
    if ($cmd=="LIST") {
        $sql = "SELECT * FROM devices" ;
        $srch = $conn->query($sql);
        
        if ($srch->num_rows > 0) {
            $first = true;
            echo '{"devices" : [';
            while($t = $srch->fetch_assoc()) {
                if ($first==false)
                    echo ",";
                $rowJSON = json_encode($t);
                echo $rowJSON;
                $first=false;
            }
            echo ']}';

        } // end of rows found

    } // end of LIST command

    if ($cmd=="GROUPS") {
        $gid = filter_input(INPUT_GET, "gid", FILTER_SANITIZE_STRING);

        if (empty($gid)) {
            $sql = "SELECT * FROM groups" ;
        }
        else {
            $sql = "SELECT * FROM groups WHERE groupID='".$gid."'" ;
        }
        $srch = $conn->query($sql);
        
        if ($srch->num_rows > 0) {
            $first = true;
            echo '{"devices" : [';
            while($t = $srch->fetch_assoc()) {
                if ($first==false)
                    echo ",";
                $rowJSON = json_encode($t);
                echo $rowJSON;
                $first=false;
            }
            echo ']}';

        } // end of rows found

    } // end of GROUPS command

} // GET

$conn->close();

?>
