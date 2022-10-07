import json

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.optim as optim
import wandb
from tqdm import tqdm

from vid2bp.nets.loss import loss
from test import test

with open('config/parameter.json') as f:
    json_data = json.load(f)
    param = json_data.get("parameters")
    hyper_param = json_data.get("hyper_parameters")
    channels = json_data.get("parameters").get("in_channels")


def train(model_n, model, device, train_loader, test_loader, epochs):
    ''' - wandb setup '''
    wandb.init(project="VBPNet", entity="paperchae")

    ''' loss function '''
    if model_n == 'Unet':
        loss_mse = torch.nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.00001)
    elif model_n == 'VBPNet':
        loss_neg = loss.NegPearsonLoss().to(device)
        loss_d = loss.dbpLoss().to(device)
        loss_s = loss.sbpLoss().to(device)
        """optimizer"""
        optimizer = optim.AdamW(model.parameters(), lr=hyper_param["learning_rate"],
                                weight_decay=hyper_param["weight_decay"])
        """scheduler"""
        scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=hyper_param["gamma"])
    else:
        print('not supported model name error')
        return

    print('batchN :', train_loader.__len__())
    model_save_cnt = 0
    cost_arr = []
    test_cost_arr = []
    for epoch in range(epochs):
        avg_cost = 0
        cost_sum = 0
        if model_n == 'Unet':
            model.train()
            with tqdm(train_loader, desc='Train', total=len(train_loader), leave=True) as train_epoch:
                idx = 0
                for X_train, Y_train in train_epoch:
                    idx += 1
                    optimizer.zero_grad()
                    hypothesis = torch.squeeze(model(X_train))
                    cost = loss_mse(hypothesis, Y_train)
                    train_epoch.set_postfix(loss=cost.item())
                    cost.backward()
                    optimizer.step()
                    cost_sum += cost
                    avg_cost = cost_sum / idx
                    cost_arr.append(avg_cost)
                    wandb.log({'Train MSE Loss': cost}, step=epoch)
                cost_arr.append(avg_cost.__float__())
            total_loss = loss_mse

        elif model_n == 'VBPNet':
            model.train()
            with tqdm(train_loader, desc='Train', total=len(train_loader), leave=True) as train_epochs:
                idx = 0
                for X_train, Y_train, d, s in train_epochs:
                    idx += 1
                    hypothesis = torch.squeeze(model(X_train)[0])
                    pred_d = torch.squeeze(model(X_train)[1])
                    pred_s = torch.squeeze(model(X_train)[2])
                    optimizer.zero_grad()

                    '''Negative Pearson Loss'''
                    neg_cost = loss_neg(hypothesis, Y_train)
                    '''DBP Loss'''
                    d_cost = loss_d(pred_d, d)
                    '''SBP Loss'''
                    s_cost = loss_s(pred_s, s)

                    '''Total Loss'''
                    cost = neg_cost + d_cost + s_cost
                    cost.backward()
                    optimizer.step()

                    cost_sum += cost
                    avg_cost = cost_sum / idx
                    train_epochs.set_postfix(_=avg_cost.item(), n=neg_cost.item(), d=d_cost.item(), s=s_cost.item())
                    wandb.log({"Train Loss": cost,
                               "Train Negative Pearson Loss": neg_cost,  # },step=epoch)
                               "Train Systolic Loss": s_cost,
                               "Train Diastolic Loss": d_cost}, step=epoch)

                scheduler.step()
                # train loss array
                cost_arr.append(avg_cost.__float__())
            total_loss = [loss_neg, loss_d, loss_s]
        if epoch % 1 == 0:
            test_c = test(model_n, model=model, test_loader=test_loader, loss=total_loss, idxx=epoch)

            test_idx = epoch + 1
            # test loss array
            test_cost_arr.append(test_c.__float__())
            # if current test loss < prev test loss:
            #   save model
            if test_idx == 1:
                test_prev_c = test_c
            else:
                test_prev_c = test_cost_arr[-2]
            # save the model only when train and test loss are lower than prior epoch
            if (cost.__float__() < avg_cost.__float__()) and (test_c.__float__() < test_prev_c.__float__()):
                print('current train cost :', cost.__float__(), '/ avg_cost :', avg_cost.__float__(), ' >> trained :',
                      avg_cost.__float__() - cost.__float__())
                print('current test cost :', test_c.__float__(), '/ prev test cost :', test_prev_c.__float__(),
                      ' >> trained :', test_prev_c.__float__() - test_c.__float__())
                dataset = 'uci'
                channel = channels['sixth']
                torch.save(model,
                           param["save_path"] + 'model_' + dataset + '_(' + str(
                               channel[-1]) + ')_Unet.pt')
                model_save_cnt += 1
    print('model saved cnt :', model_save_cnt)
    print('cost :', cost_arr[-1])

    t_val = np.array(range(len(cost_arr)))
    plt.title('Neg Pearson corr + SBP modMAE + DBP modMAE')
    plt.plot(t_val, cost_arr, label='Train loss')
    plt.plot(t_val, test_cost_arr, linestyle='--', label='Test loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
