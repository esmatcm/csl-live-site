<?php
header('Content-Type: application/json');
$data = array('message' => 'Hello from PHP!');
echo json_encode($data);
?>