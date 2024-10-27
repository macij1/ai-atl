opts = detectImportOptions('combined_citation_connections.csv');
opts.VariableNames = {'source_paper', 'cited_by'};
opts.SelectedVariableNames = {'source_paper', 'cited_by'};
opts.Delimiter = ',';
opts.VariableTypes = {'string', 'string'};

data = readtable('combined_citation_connections.csv', opts);

sources = string(data.source_paper);
cited = string(data.cited_by);

sources = strtrim(sources);
cited = strtrim(cited);

sources(ismissing(sources)) = "";
cited(ismissing(cited)) = "";

papers = unique([sources; cited], 'stable');
papers = papers(papers ~= "");  % Remove empty strings if any

numPapers = length(papers);
papersCell = cellstr(papers);
paperMap = containers.Map(papersCell, 1:numPapers);

A = sparse(numPapers, numPapers);

display(sources)
for i = 1:height(data)
    srcIdx = paperMap(sources{i});
    tgtIdx = paperMap(cited{i});
    A(tgtIdx, srcIdx) = A(tgtIdx, srcIdx) + 1;
end

colSum = sum(A, 1);
danglingNodes = (colSum == 0); 
A(:, danglingNodes) = 1 / numPapers;
A(:, colSum > 0) = A(:, colSum > 0) ./ colSum(colSum > 0);

d = 0.85;  
tolerance = 1e-6;  
pagerankVec = ones(numPapers, 1) / numPapers;
delta = 1;

while delta > tolerance
    newPagerankVec = (1 - d) / numPapers + d * A * pagerankVec;
    delta = norm(newPagerankVec - pagerankVec, 1);
    pagerankVec = newPagerankVec;
end

[~, idx] = sort(pagerankVec, 'descend');
rankedPapers = papers(idx);

disp('Top papers by PageRank:');
disp(rankedPapers());

ranks = (1:length(rankedPapers))';
disp(length(rankedPapers))

results = table(ranks, rankedPapers, pagerankVec(idx), ...
    'VariableNames', {'Rank', 'Paper', 'PageRank'});

writetable(results, 'pagerank_results.csv');

disp('First few results saved to CSV:');
head(results)

outputPath = 'C:\Users\seyon\Desktop\Programming Projects\i-cite\pagerank_results.csv';
writetable(results, outputPath);


