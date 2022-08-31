package main

import (
	"BHgwLoginTool/src/util"
	"crypto/hmac"
	"crypto/md5"
	"crypto/sha1"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"runtime"
	"time"
)

const acId = "62"

func _exitIfErr(err error) {
	if err != nil {
		log.Fatalf("[ERR]%v\n", err)
	}
}

func _getChallengeUrl(username string) string {
	return "https://gw.buaa.edu.cn/cgi-bin/get_challenge?callback=jQuery1124040520953767391155_4059734400000&username=" + username
}

func _getSrunPortalUrl(paramsMap map[string]string) string {
	params := url.Values{}
	for k, v := range paramsMap {
		params.Add(k, v)
	}
	return "https://gw.buaa.edu.cn/cgi-bin/srun_portal?" + params.Encode()
}

func getTokenIp(username string) (string, string) {
	challengeUrl := _getChallengeUrl(username)
	req, err := http.NewRequest("GET", challengeUrl, nil)
	_exitIfErr(err)
	req.Header.Add("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15")
	resp, err := (&http.Client{}).Do(req)
	_exitIfErr(err)
	body, err := io.ReadAll(resp.Body)
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		_exitIfErr(err)
	}(resp.Body)
	_exitIfErr(err)
	jsonStr := fmt.Sprintf("%s", body)
	jsonStr = jsonStr[43 : len(jsonStr)-1]
	var jsonMap map[string]interface{}
	err = json.Unmarshal([]byte(jsonStr), &jsonMap)
	_exitIfErr(err)
	token, ip := jsonMap["challenge"].(string), jsonMap["client_ip"].(string)
	return token, ip
}

func getEncryptedHmd5(token, password string) string {
	hmacObj := hmac.New(md5.New, []byte(token))
	hmacObj.Write([]byte(password))
	hmd5 := fmt.Sprintf("%x", hmacObj.Sum(nil))
	return hmd5
}

func getEncryptedInfo(token, username, password, ip string) string {
	infoJsonStr := fmt.Sprintf(`{"username":"%s","password":"%s","ip":"%s","acid":"%s","enc_ver":"srun_bx1"}`, username, password, ip, acId)
	return "{SRBX1}" + util.Base64(util.XEncode(infoJsonStr, token))
}

func getEncryptedChksum(token, username, hmd5, info, ip string) string {
	chkstr := token + username
	chkstr += token + hmd5
	chkstr += token + acId
	chkstr += token + ip
	chkstr += token + "200"
	chkstr += token + "1"
	chkstr += token + info
	chksum := fmt.Sprintf("%x", sha1.Sum([]byte(chkstr)))
	return chksum
}

func login(username, chksum, hmd5, info, ip string) string {
	paramsMap := map[string]string{
		"callback":     "jQuery1124040520953767391155_4059734400000",
		"action":       "login",
		"username":     username,
		"password":     "{MD5}" + hmd5,
		"ac_id":        acId,
		"ip":           ip,
		"chksum":       chksum,
		"info":         info,
		"n":            "200",
		"type":         "1",
		"os":           runtime.GOOS,
		"name":         runtime.GOOS,
		"double_stack": "0",
		"_":            fmt.Sprintf("%d", time.Now().Unix()*1000),
	}
	resp, err := http.Get(_getSrunPortalUrl(paramsMap))
	_exitIfErr(err)
	body, err := io.ReadAll(resp.Body)
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		_exitIfErr(err)
	}(resp.Body)
	bodyStr := fmt.Sprintf("%s", body)
	bodyStr = bodyStr[43 : len(bodyStr)-1]
	var bodyJsonMap map[string]interface{}
	err = json.Unmarshal([]byte(bodyStr), &bodyJsonMap)
	_exitIfErr(err)
	if bodyJsonMap["error"].(string) != "ok" {
		return bodyJsonMap["error_msg"].(string)
	}
	return fmt.Sprintf("%s", bodyJsonMap["res"].(string))
}

func main() {
	startTime := time.Now()

	//i = info(JSONstringified, token)
	//hmd5 = md5(password, token)
	//chksum = sha1(chkstr)

	username, password := "", ""
	token, ip := getTokenIp(username)
	info := getEncryptedInfo(token, username, password, ip)
	hmd5 := getEncryptedHmd5(token, password)
	chksum := getEncryptedChksum(token, username, hmd5, info, ip)
	loginRes := login(username, chksum, hmd5, info, ip)

	endTime := time.Now()
	fmt.Printf("%s\n", loginRes)
	fmt.Printf("[In %.2fs]\n", endTime.Sub(startTime).Seconds())
	os.Exit(0)
}
