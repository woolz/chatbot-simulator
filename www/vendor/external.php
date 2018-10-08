<?php
header('Content-Type: application/json');
$message = $_GET['message'];
$input = $_GET['input_value'];
$section = $_GET['section'];
$record = $_GET['record'];
$retry = $_GET['retry'];

$url = 'http://127.0.0.1:5000/chatbot-demo/api/v1/section='.$section.'&message='.urlencode($message).'&input_value='.$input.'&retry='.$retry.'&record='.$record.'';  
$response = (file_get_contents($url)); 
print_r($response);
?>
