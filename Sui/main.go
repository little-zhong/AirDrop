package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"github.com/coming-chat/go-sui/account"
	"github.com/coming-chat/go-sui/client"
	"github.com/coming-chat/go-sui/types"
)

type Account []struct {
	Account struct {
		Address  string `json:"address"`
		Mnemonic string `json:"mnemonic"`
	} `json:"account"`
}

func main() {
	jsonFile, _ := os.Open("../sui_wallet.json")
	defer jsonFile.Close()
	jsonData, _ := ioutil.ReadAll(jsonFile)
	var account_data Account
	json.Unmarshal(jsonData, &account_data)

	cli, _ := client.Dial("http://localhost:9000")
	ctx := context.Background()
	var main_address, _ = types.NewAddressFromHex(account_data[0].Account.Address)

	for index, value := range account_data {
		// 归集代币至主账户
		if index == 0 {
			continue
		}
		acc, _ := account.NewAccountWithMnemonic(value.Account.Mnemonic)
		owned_address, _ := types.NewHexData(acc.Address)
		coin_obj_list, _ := cli.GetSuiCoinsOwnedByAddress(ctx, *owned_address)
		for _, coin_info := range coin_obj_list {
			if coin_info.Balance > uint64(1000) {
				fmt.Println(coin_info.Reference.ObjectId, coin_info.Balance, *owned_address)
				txnBytes, err := cli.TransferSui(
					ctx,
					*owned_address,
					*main_address,
					coin_info.Reference.ObjectId,
					uint64(float64(coin_info.Balance)*0.9),
					1e2,
				)
				if err != nil {
					fmt.Println("err", err)
				}
				signedTxn := txnBytes.SignWith(acc.PrivateKey)
				Response_raw, _ := cli.ExecuteTransaction(ctx, *signedTxn, "WaitForLocalExecution")
				log.Println(Response_raw.EffectsCert.Certificate.TransactionDigest)
			}
		}
	}
}
