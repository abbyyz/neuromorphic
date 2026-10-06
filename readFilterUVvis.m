%% Lamp Data/smoothing 

lamp = readmatrix('2019-05-21_XP447 compilation for Customer Use.xlsx','Range','A3:B1911');
% lamp = lamp(1:1911,:); 
lamp(:,1) = round(lamp(:,1));

lambda = 200:1000; 
int = zeros(1,length(lambda)); 

for i = 1 : length(lambda)

    boop  = lamp(lamp(:,1) == lambda(i),:); 
    meanInt = mean(boop(:,2)); 
    int(i) = meanInt; 

end

energy = ((6.63e-34 * 3e8)./(lambda*1e-9));
spectralIrr = int .* energy;
plot(lambda,spectralIrr);

% figure()
% plot(lamp(:,1),lamp(:,2),'d')

%% Read in UVVis Data
files = dir('*.csv'); 
data = extractfield(files,'name'); 

%Convert file names to string 

data = string(data); 
% filt = contains(data,'MFM');
% data = data(filt);

% %Keep Only Pt Data 
% Pt = ~contains(data,'try'); 
% Pt_data = data(Pt); 
% Pt_data = data;
colors = orderedcolors("gem12");
totalData = []; 

for i = 1 : length(data)

    %read in data 
    uvVis = readmatrix(data(i),'Range','A3:F803');

    % %plot data together and average
    plot(uvVis(:,1),mean(uvVis(:,4:2:end),2),'LineWidth', 1.5);
    hold on 
    ylabel('T')
    xlim([200 1000])
    xlabel('Wavelength(nm)')

    % totalData = [totalData mean(uvVis(:,4:2:end),2)/100];
    totalData = [totalData mean(uvVis(:,4:2:end),2)/100];

end


%% Mulitplay Together for filters 


integratedI = zeros(1,4); 
figure()
for i = 1:1

    %multiply by intenisty 
    abs_lamp = flip(totalData(:,i))'.*spectralIrr; 

    %integrate
    integratedI(i) = trapz(lambda,abs_lamp);
    plot(lambda,abs_lamp,'LineWidth',1.75);
    hold on 
    % scatter([i],integratedI(i)/3.45011e-13,'d','filled')
    % hold on 

end

noFilt = trapz(lambda,spectralIrr);

figure()
scatter(1:2,integratedI(1:2)/noFilt,'d')
% ylim([0 1.1])
% xlim([0.7 4.3])
set(gcf,'color','w')
ylabel('Integrated Spectral Irradiance (W)')

%% Mulitplay MO and TiN with 

%Read in TiN and Mo data
TiN = readmatrix("TiN_10nmHZO.csv",'Range','A3:F803');
Mo = readmatrix("Mo_10nmHZO.csv",'Range','A3:F803');

%average uv vis data 
% TiN = mean(TiN(:,4:2:end));
% Mo = mean(Mo(:,4:2:end));

integratedI_Mo = zeros(1,4); 
integratedI_TiN = zeros(1,4); 
figure(1)
figure(2)
for i = 1:4

    %multiply by intenisty 
    abs_lamp_TiN = flip(totalData(:,i))'.*spectralIrr .* flip(TiN(:,4))'; 
    abs_lamp_Mo = flip(totalData(:,i))'.*spectralIrr .* flip(Mo(:,4))'; 

    figure(1)
    plot(lambda,abs_lamp_TiN,'LineWidth',1.5);
    ylabel('Weighted Abs (W/nm)')
    hold on 
    ylim([-0.1e-16 7e-16]);

    figure(2)
    plot(lambda,abs_lamp_Mo,'LineWidth',1.5);
    ylabel('Weighted Abs (W/nm)')
    hold on 
    ylim([-0.1e-16 7e-16]);

    %integrate
    integratedI_Mo(i) = trapz(lambda,abs_lamp_Mo);
    integratedI_TiN(i) = trapz(lambda,abs_lamp_TiN);
    % plot(lambda,abs_lamp,'LineWidth',1.75);
    % hold on 
    % figure(1)
    % scatter([1],integratedI_TiN(i),'d','filled')
    % scatter([2],integratedI_Mo(i),'d','filled')
    % hold on 



end

figure(1)
hold on 
yyaxis right 
plot(lambda,flip(TiN(:,4))','LineWidth',1.5);
ylabel('Abs (a.u.)');
xlabel('Wavelength(nm)');
ylim([0 0.5]);

figure(2)
hold on 
yyaxis right
plot(lambda,flip(Mo(:,4))','LineWidth',1.5);
ylabel('Abs (a.u.)');
xlabel('Wavelength(nm)');
ylim([0 0.5]);

% 
% figure()
% scatter(1:4,integratedI/max(integratedI),'d')
% ylim([0 1.1])
% xlim([0.7 4.3])
% set(gcf,'color','w')
% ylabel('Integrated Spectral Irradiance (W)')

%% plot

for i = 1:4

    scatter([2], integratedI_Mo(i)/9.85e-14,55,'d','filled','MarkerEdgeColor',colors(i,:), 'MarkerFaceColor',colors(i,:));
    hold on 
    scatter([1], integratedI_TiN(i)/8.20244e-14,55,'d','filled','MarkerEdgeColor',colors(i,:), 'MarkerFaceColor',colors(i,:));

end

ylabel('Integrated Weighted Abs (W)')
xlim([0.5 2.5])



