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
	//获取主账户的代币余额
	var main_address_balance uint64
	coin_obj_list, _ := cli.GetSuiCoinsOwnedByAddress(ctx, *main_address)
	for _, coin_info := range coin_obj_list {
		main_address_balance += coin_info.Balance
	}
	// 每个账户能分配到的代币
	coin_per_account := uint64(float64(main_address_balance/uint64(len(account_data)+1)) * 0.9)
	// log.Println("每个账户获得代币:", coin_per_account)
	// 主账户发放代币给其他账户
	acc, _ := account.NewAccountWithMnemonic(account_data[0].Account.Mnemonic)
	for index, value := range account_data {
		if index == 0 {
			continue
		}
		owned_address, _ := types.NewHexData(value.Account.Address)
		coin_obj_lists, _ := cli.GetSuiCoinsOwnedByAddress(ctx, *main_address)
		var sui_obj_list []any
		for _, coin_info := range coin_obj_lists {
			if coin_info.Balance > uint64(1e3) {
				sui_obj_list = append(sui_obj_list, coin_info.Reference.ObjectId)
			}
		}

		for _, coin_info := range coin_obj_lists {
			if coin_info.Balance > uint64(1e3) {
				fmt.Println("转移代币至:", *owned_address, coin_per_account)
				resp := types.TransactionBytes{}
				txnBytes := cli.CallContext(
					ctx,
					&resp,
					"sui_paySui",
					*main_address,
					sui_obj_list,
					[]any{*owned_address},
					[]any{coin_per_account},
					1e3,
				)
				if txnBytes != nil {
					fmt.Println("err", txnBytes)
				}
				signedTxn := resp.SignWith(acc.PrivateKey)
				Response_raw, _ := cli.ExecuteTransaction(ctx, *signedTxn, "WaitForLocalExecution")
				log.Println(Response_raw.EffectsCert.Certificate.TransactionDigest)
				break
			}
		}
	}
}
