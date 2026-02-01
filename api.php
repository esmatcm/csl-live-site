<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$matchId = $_GET['id'] ?? '';
if (!$matchId) {
    echo json_encode(["error" => "no_id"]);
    exit;
}

$apiKey = '735d0b4e485a431db7867a42b0dda855';
$cacheFile = "cache/match_" . $matchId . ".json";
$lockFile = "cache/api_limit.lock";

// 1. 15s 快取檢查
if (file_exists($cacheFile) && (time() - filemtime($cacheFile) < 15)) {
    echo file_get_contents($cacheFile);
    exit;
}

// 2. 100/min 限流檢查 (間隔 0.6s)
if (file_exists($lockFile) && (time() - filemtime($lockFile) < 1)) {
    // 雖然 100/min 是 0.6s，但為了穩健，並發間隔設為 1s
    if (file_exists($cacheFile)) {
        echo file_get_contents($cacheFile); // 限流時回傳舊快取
        exit;
    }
}

// 3. 發起外部請求
touch($lockFile);
$url = "https://api.football-data.org/v4/matches/" . $matchId;
$opts = [
    "http" => [
        "method" => "GET",
        "header" => "X-Auth-Token: " . $apiKey . "\r\n",
        "ignore_errors" => true
    ]
];
$context = stream_context_create($opts);
$response = file_get_contents($url, false, $context);

// 4. 處理回傳並寫入快取
if (!str_contains($http_response_header[0], "200")) {
    http_response_code(429);
    echo json_encode(["error" => "rate_limited_or_error", "status" => $http_response_header[0]]);
} else {
    if (!is_dir('cache')) mkdir('cache');
    file_put_contents($cacheFile, $response);
    echo $response;
}
?>
